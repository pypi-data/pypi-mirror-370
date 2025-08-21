import numpy as np
import os
import pandas as pd

class MSM_Modeller():

    def __init__(self,candidate_states,reduced_coordinates,frame_scale):
        '''A module for evaluating and modelling the candidate states and subsequent MSM of an emebddingspace.

        
        Parameters
        ----------


        Returns
        -------


        Notes
        -----


        Examples
        --------

        '''
        self.candidate_states=candidate_states if candidate_states is not None else None 
        self.reduced_coordinates=reduced_coordinates if reduced_coordinates is not None else None 
        self.frame_scale=frame_scale if frame_scale is not None else None 

    def rmsd_from_centers(self, X, labels, centers):
        results = []
        for k in np.unique(labels):
            m = (labels == k)  # mask frames belonging to cluster k
            d = np.linalg.norm(X[m] - centers[int(k)], axis=1)
            rmsd = float(np.sqrt(np.mean(d**2)))
            results.append((int(k), rmsd))
        results=np.array(results)
        return results

    def evaluate_cohesion(self,candidate_states=None,reduced_coordinates=None,frame_scale=None,window_size=None):
        '''evaluate whether trajectories are temporally settling into the candidate states
        
        Paramters
        ---------
        candidatestates=arraylike,default=mdsa_tools.Analysis.cluster_embeddingspace(),shape=(number_of_systems_)
            A list of arrays holding, each array in every system contains the cluster assignments and labels returned
            from the system analysis module's preform_clust_opt() operation.
        
        reduced coordinates =arraylike,shape=(n_samples,2)
            The results of either Principal Components Analysis or UMAP reduction to 2 new dimensions.
        
        frame_scale:list of int, optional
            A list holding integer counts of the number of frames in each replicate. 
            Default is (([80] * 20) + ([160] * 10)) * 2.
        
        
            
        
        Returns
        -------



        Notes
        -----




        Examples
        --------



        
        '''
        candidate_states=candidate_states if candidate_states is not None else self.candidate_states
        reduced_coordinates=reduced_coordinates if reduced_coordinates is not None else self.reduced_coordinates
        frame_scale=frame_scale if frame_scale is not None else self.frame_scale
        window_size = window_size if window_size is not None else 10

        cords_per_sys=np.array_split(reduced_coordinates,len(candidate_states))


        rmsd_df_per_system=[]


        for i in range(len(candidate_states)):#iterate through system
            labels,centers = candidate_states[i][0],candidate_states[i][1] #grab labels and center of current system
            current_coordinates=cords_per_sys[i]

            rmsd_window_all=[]            
            
            window_iterator=0
            num_windows=np.max(frame_scale)//window_size
            print(f'\nwindow_iterator {window_iterator}, num_windows {num_windows}')
            start=0
            for j in range(num_windows):
                start+=window_size*j
                window_df_all=[]

                for k in range(len(frame_scale)):
                    
                    current_replicate_length=frame_scale[k]
                    if j * window_size >= current_replicate_length:
                        # keep 'start' aligned for the next replicate
                        start += current_replicate_length
                        # print(f"SKIP rep={k}, win={j} (rep_len={current_replicate_length})")
                        continue
                    end=start+window_size
                    rmsd_results = self.rmsd_from_centers(
                    current_coordinates[start:end,:],
                    labels[start:end],
                    centers
                    )
                    print(f"current_window:{j}, current replicate:{k}")
                    print(f"current_start:{start}, current end:{end}")
                    windowdf=pd.DataFrame(rmsd_results,columns=('cluster','rmsd'))
                    windowdf['window'] = j
                    windowdf["system"] = i
                    windowdf["length"] = current_replicate_length
                    window_df_all.append(windowdf)
                    start+=current_replicate_length#move forward in replicate 

                start=0

                rmsd_concat = pd.concat(window_df_all, ignore_index=True)
                avg_equal_by_window = (rmsd_concat
                .groupby(['length','system','window','cluster'])['rmsd'].mean())     # mean within cluster
                rmsd_window_all.append(avg_equal_by_window)
                
            
            rmsd_window_all=pd.concat(rmsd_window_all)
            rmsd_df_per_system.append(rmsd_window_all)
            
        rmsd_df_per_system=pd.concat(rmsd_df_per_system)     
        print(rmsd_df_per_system) 
        return rmsd_df_per_system

    def create_transition_probability_matrix(self,labels=None,frame_list=None,lag=None):
        '''Create probability matrix from input data (returns, and updates class attribute)

        Parameters
        ----------
        labels:arraylike,shape=(n_labels,)
            A list of labels pertaining to frames of molecular dynamics trajectories assigned particular substates

        frame_list: listlike,shape=(data,)
            A list of integers representing the number of frames present in each replicate. This should be in the order
            of which the various versions of the system, and replicates where concatenated. 

        
        Returns
        -------
        transition_probability_matrix:arraylike;shape=(n_states+1,n_states+1)
            A transition probability matrix created from the list of labels. Diagonals indicate
            if it is likely to stay in the same state and off diagonals mark probabilities of transitions



        
        Notes
        -----
        Much in the spirit of our original matrices the first row and column of theese matrices contain
        indexes mainly for ease of use and manipulation. Yes, in theory pandas dataframes could streamline this process
        but, numpy arrays are just that much more efficient in most use cases,



        Examples
        --------

        

        '''


        labels=labels if labels is not None else self.labels
        frame_list=frame_list if frame_list is not None else self.frame_list
        lag=lag if lag is not None else 1

        #extract unique states and initiate transiiton probability matrix
        unique_states=np.unique(labels)
        number_of_states=len(unique_states)
        transtion_prob_matrix=np.zeros(shape=(number_of_states,number_of_states))
        
        iterator=0
        for trajectory_length in frame_list: # iterate through 
            current_trajectory=labels[iterator:iterator+trajectory_length]
            iterator=iterator+trajectory_length #update this 

            for i in range(current_trajectory.shape[0]-lag):
                current_state=current_trajectory[i]
                next_state = current_trajectory[i+lag]
                transtion_prob_matrix[current_state, next_state] += 1

        row_sums = transtion_prob_matrix.sum(axis=1, keepdims=True)

        transition_probs = np.divide(
                    transtion_prob_matrix, row_sums,
                    out=np.zeros_like(transtion_prob_matrix), #because we dont want to divide by zero!
                    where=row_sums>0
                )

        final_transition_prob_matrix=np.zeros(shape=(number_of_states+1,number_of_states+1))
        final_transition_prob_matrix[1:,1:]=transition_probs
        final_transition_prob_matrix[0,1:],final_transition_prob_matrix[1:,0]=unique_states,unique_states

        self.transition_probability_matrix=final_transition_prob_matrix

        return final_transition_prob_matrix
    
    def evaluate_Chapman_Kolmogorov(self,transition_probability_matrix=None,n=None,labels=None,original_lag=None):
        '''evaluate if the chapman kolmogorov test evaluates to true

        Parameters
        ----------
        n:int,default=4
            The original number of lags we used to compute the transition probability matrix
        
        transition_proability_matrix:arraylike,shape=(n_states+1,n_states+1),

        n:int,default=4
            The time lag we are using to compute our labels

        labels:arraylike,default=self.labels
            The list of labels we are using for the labeling of data from trajectories. 
        
        original_lag:int:default=1


        Notes
        -----

        
        Returns
        -------



        Examples
        --------
        
        
        '''

        transition_probability_matrix=transition_probability_matrix if transition_probability_matrix is not None else self.create_transition_probability_matrix()
        original_lag=original_lag if original_lag is not None else 1
        n = n if n is not None else 4
        labels=labels if labels is not None else self.labels

        transition_prob_data=transition_probability_matrix[1:,1:]
        post_timestep_data=np.linalg.matrix_power(transition_prob_data,n)
        transition_probability_matrix[1:,1:]=post_timestep_data

        total_lag=original_lag*n
        matrix_from_total_lag = self.create_transition_probability_matrix(lag=total_lag)
        diff=matrix_from_total_lag[1:,1:]-transition_probability_matrix[1:,1:]
        frob = np.linalg.norm(diff, ord='fro')

        return frob