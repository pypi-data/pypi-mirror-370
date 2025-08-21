import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import numpy as np
import os
from sklearn.decomposition import PCA
from mdsa_tools.Viz import visualize_reduction
import pandas as pd
import matplotlib.cm as cm
import umap
import os

class systems_analysis:
    '''A big wrapper for conveniently storing a lot of our analysis methods
    '''

    def __init__(self,systems_representations=None,replicate_distribution=None):
        '''
        Parameters
        ----------
        systems_representations:list, expected=list[array_1,...,array_n-1] where each array is an np.ndarray with shape=(n_frames,n_residues,n_residues)
            Each array should have the shape as described above, where each frame has an adjacency matrix of pairwise
            comparisons between all residues. The only axis that can differ between arrays is the number of frames (n_frames).
        
        frame_list: listlike,shape=(data,)
            A list of integers representing the number of frames present in each replicate. This should be in the order
            of which the various versions of the system, and replicates where concatenated.
        

        Returns
        -------
        None its an init

        


        Notes
        -----
        -automatically will convert list of arrays into a feature matrix so its easy to build it in
        -Additionally this for now expects systems of the same size for automation, if you want to run some of the downstream tasks
        you will most likely have to do it yourself if you are trying to analyze differently sized (in terms of frames) systems
        -Although since really this is a more general systems perspective on molecular dynamics its a great bouncing point for any systems project you may
        have in mind


        Examples
        --------
        '''
        
        self.num_systems=len(systems_representations) #this is useful later on for when we are doing system_specific operations
        self.systems_representations=systems_representations
        self.indexes = systems_representations[0][0, 0, 1:] #bc list then 3d array
        
        if replicate_distribution is not None:
            self.replicate_distribution=replicate_distribution
            
        if replicate_distribution is None:
            self.replicate_distribution=np.arange(0,systems_representations[0].shape[0])
        
        return


    #pre-processing
    def replicates_to_featurematrix(self,arrays=None)->np.ndarray:
        """returns an array formatted for kmeans clustering with scipy

        Parameters
        ----------
        arrays:list, expected=list[array_1,...,array_n-1] where each array is an np.ndarray with shape=(n_frames,n_residues,n_residues)
            Each array should have the shape as described above, where each frame has an adjacency matrix of pairwise
            comparisons between all residues. The only axis that can differ between arrays is the number of frames (n_frames).

            
        Returns
        -------
        array:np.ndarray,shape=(sum(n_frames),n_residues*n_residues) where the sum of n_frames refers to the total number of frames.
            Each row of the new matrix represents a flattened adjacency matrix for each frame, and the frames are stacked
            in such a way that each of the original arrays follow each other sequentially.


        Examples
        --------
        >>>CCU_GCU_fulltraj=np.load('/zfshomes/lperez/presentation_directory/CCU_GCU_Trajectory_array.npy',allow_pickle=True)
        >>>CCU_CGU_fulltraj=np.load('/zfshomes/lperez/presentation_directory/CCU_CGU_Trajectory_array.npy',allow_pickle=True)
        >>>arrays=[CCU_GCU_fulltraj,CCU_CGU_fulltraj]
        >>>Kmeans_replicatearray=format_replicate_for_clust(arrays)
            
            
        Notes
        -----
        First we concatenate all of our arrays into one large array. This does however rely on the premise that the only difference
        between our arrays is the number of frames (n_frames). This holds true conceptually because if we have a different
        number of pairwise residue comparisons we would not have comparable networks, or "systems".

        The goal is to flatten each adjacency matrix into a 1 dimensional vector and then stack all frames.
        This results in the expected formatting for scipy's kmeans clustering implementation where each .
        
        """
        arrays = arrays if arrays is not None else self.systems_representations
        
        #Concatenate arrays and define list to hold reformatted arrays
        try:
            concatenated_array=np.concatenate((arrays))
        except(ValueError, TypeError):
            print("its really best if you input a list but the program will move on with the assumption you have given just a single arrray as input")
            concatenated_array=np.asarray(arrays)

        final_frames=[]
        frame_num, n_residues, _ = concatenated_array.shape

        # Get indices for upper triangle (excluding diagonal)
        triu_idx = np.triu_indices(n_residues - 1, k=1)  # -1 due to [1:,1:] slice below


        final_frames = []
        for i in range(frame_num):
            current_frame = np.copy(concatenated_array[i, 1:, 1:])
            # Extract upper triangle only
            flattened = current_frame[triu_idx]
            final_frames.append(flattened)

        final_frames = np.vstack(final_frames).astype(np.float32)
        self.feature_matrix=final_frames#set global var as well

        return final_frames

    #Analyses
    def cluster_system_level(self,outfile_path=None, max_clusters=None,data=None):
        '''
        Parameters
        ----------
        data:np.ndarray,shape=(n_sample,featuresures),
            A feature matrix of any kind, hopefully one provided from the rest of the pipeline but in theory, this is 
            just a scikit learn wrapper so you can plug anything you want really

        max_clusters:int,default=10
            The maximum number of initial centroids we are iterating through while optimizing sillohuette scores and elbow plots.
        
        outfile_path:str,default=os.getcwd()
            The path to where we would like to save the outputted labels (frame assignments of K-means)
        
        data:arraylike,shape=(n_samples,featuresures)
            Ideally this is the feature matrix provided as input at the top of the workflow but, its provided as a parameter incase
            you'd like to use theese in your own way.
        

        Returns
        ----------
        (optimal_k_silhouette_labels,optimal_k_elbow_labels,centers_sillohuette,centers_elbow):tuple,shape=(4)
            A tuple holding all of the objects created by the clustering of our systems representations. In order from left to right
            the labels from the optimal number of initial centroids as defined by sillohuette score analysis; then the labels from optimal
            clustering as defined the the elbow plots, as well as the centroids found for the sillohuette centers and elbow centers.
        
            
        Notes
        -------
        We do assume you have atleast 10 frames worth of data... clustering any less than that
        is a little out of the scope of this simple euclidean distance K-means clustering implementation.
        
        Examples
        ---------

        
        '''
        max_clusters=max_clusters if max_clusters is not None else 10
        data = data if data is not None else self.feature_matrix
        outfile_path=outfile_path if outfile_path is not None else os.getcwd()
        optimal_k_silhouette_labels,optimal_k_elbow_labels,centers_sillohuette,centers_elbow=self.preform_clust_opt(outfile_path=outfile_path,data=data,max_clusters=max_clusters)


        return optimal_k_silhouette_labels,optimal_k_elbow_labels,centers_sillohuette,centers_elbow
    
    def reduce_systems_representations(self,feature_matrix=None,method=None,n_components=None,min_dist=None,n_neighbors=None):
        '''
        Parameters
        ----------
        feature_matrix:np.ndarray,shape=(sum(n_frames),n_residues*n_residues) where the sum of n_frames refers to the total number of frames.
            Each row of the new matrix represents a flattened adjacency matrix for each frame, and the frames are stacked
            in such a way that each of the original arrays follow each other sequentially.
        
            
        n_components:int,default=2
            The number of principal components you would like to reduce your dataset down to
        
            
        str:outfile_path,default=os.getcwd()
            path to where you would like to save your visualization
        
        min_dist:float,default=0.5
            This is a UMAP-specific parameter. It controls how tightly UMAP is allowed to pack points together. 
            Lower values will preserve more of the local clusters in the data whereas higher values will push 
            points further apart.

        n_neighbors:int,default=900
            Another UMAP-specific parameter. It determines the number of neighboring points used in 
            local approximations of the manifold. Larger values result in more global structure being preserved.


        
        Returns
        -------
        X_pca,weights,explained_variance_ratio_

        X_PCA:np.ndarray,shape=(n_samples,n_components)
            An array returned by the PCA module in scikit-learns vs.cluster module. Essentially it is the x and y coordinates
            of every sample from the original feature matrix now reduced into the principal component embedding space.
            ---As in the output from scikit learns module PCA() from the cluster.vq() module check in later for link---

            In theory it should be (n_sampels,2) since we are generally reducing to two principal components but, if you choose to 
            use a different number of principal components this would be a different # thus, the signature is broad


        weights:shape=(n_samples,n_components)
            The loadings for each principal component. Theese can be thought of as eigenvector components and they are the raw values 
            they have not been **2 for magnitude measurements yet. This is a seperate function in this module called create_PCA_ranked_weights.

        explained_variance_ratio_:int,
            The explained variance ratio of the principal components. This is just a fraction since we are using two principal components
            but, if you choose to use more it would be slightly different. 
            **Check back here**    
        
       


        Notes
        -----
        You should include a pre-fix in your outfile path as the image will be saved with the ending
        "PCA_reduction" so a good example input is

        "/users/userone/desktop/project/output/test_"

        Examples
        --------

        
        '''

        if feature_matrix is not None:
            feature_matrix = feature_matrix 
        if self.feature_matrix is not None:
            feature_matrix=self.feature_matrix
        if self.feature_matrix is None:
            self.replicates_to_featurematrix()
            feature_matrix=self.feature_matrix

        n_components=n_components if n_components is not None else 2
        method = method if method is not None else 'PCA'
        min_dist = min_dist if min_dist is not None else .5
        n_neighbors= n_neighbors if n_neighbors is not None else 900

        if method=='PCA':
        
            X_pca,weights,explained_variance_ratio_=self.run_PCA(feature_matrix,n_components)
            return X_pca,weights,explained_variance_ratio_
            
        if method=='UMAP':

            # Initialize UMAP
            reducer = umap.UMAP(n_components=n_components,n_neighbors=n_neighbors,min_dist=.5)
            embedding = reducer.fit_transform(feature_matrix)

            return embedding
            
            
        elif method != 'PCA' and method != 'UMAP':
            print('No valid method supplied for dimensional reduction ')
        
    def cluster_embeddingspace(self, reduced_coordinates=None,outfile_path=None,num_systems=None,val_metric=None):
        '''
        This has been depreciated for now
        
        '''
        
        
        '''A function for looking at conformational states in embedding space

        Parameters
        ----------
        outfilepath:str
            path to save

        reduced_coordinates:np.Ndarray,default=self.reduced_coordinates,shape=
            A feature matrix to be used for analysis
        
        n:int,default=2
            number of principal components to reduce to
        
        max_clusters:int,default=10
            The defualt number

        val_metric:str,default='sillohuete'
            The validation metric you would like to use for picking an "ideal number of clusters'
            


        Returns
        -------



        Notes
        -----



        Examples
        --------

        '''

        outfile_path = outfile_path if outfile_path is not None else os.getcwd()
        num_systems = num_systems if num_systems is not None else self.num_systems
        val_metric=val_metric if val_metric is not None else 'sillohuette'
        
        if reduced_coordinates is None:
            reduced_coordinates,_,_=self.reduce_systems_representations()

        
        #grab the number of rows we need and then iterate through X_pca run kmeans and visualize using our initial values
        individual_systems=np.array_split(reduced_coordinates, num_systems,axis=0)
        print(individual_systems[0].shape)
        candidate_states_per_system=[]
        for i in individual_systems:
            optimal_k_silhouette_labels,optimal_k_elbow_labels,centers_sillohuette,centers_elbow=self.preform_clust_opt(outfile_path,data=i)
            if val_metric=='sillohuette':
                candidate_states_per_system.append([optimal_k_silhouette_labels,centers_sillohuette])
            if val_metric=='elbow':
                candidate_states_per_system.append([optimal_k_elbow_labels,centers_elbow])


        return candidate_states_per_system

    def create_pearsontest_for_kmeans_distributions(self,labels,coordinates,cluster_centers):
        '''
        Currently depreciated
        '''
        '''A function that is meant for the 

        Parameters
        ----------
        labels:listlike
            A list or array of labels that tell us which cluster each sample belongs to

        coordinates:array,shape=(n_samples,featuresures)
            An array which tells us the coordinates of each sample so we can form distributions from them and run statistical tests
            (pearson corellation coefficient)
        
        cluster_centers:listlike,shape=k
            A list of arrays which tell us the coordinates for each cluster center so that we can calculate distributions
            to them


        Returns
        -------




        Notes
        -----



        Examples
        --------


        
        '''
        distances = np.linalg.norm(coordinates - cluster_centers[labels], axis=1) #euclidean distances to centroid

        #extracting everything by the group its a part of
        dist_by_cluster = {}
        for cluster_id in np.unique(labels):
            dist_by_cluster[int(cluster_id)] = distances[labels == cluster_id]

        #find minimum distance
        lengths = [len(i) for i in dist_by_cluster.values()]
        #print(lengths)
        shortest_length = min(lengths)
        #print(shortest_length)


        #form final list
        final_distributions=[]
        for i in dist_by_cluster.values():
            current_distribution=i[0:shortest_length,]
            final_distributions.append(current_distribution)
        
        from scipy.stats import pearsonr
        import pandas as pd
        
        correlations = []

        for i in range(len(final_distributions)):
            for j in range(i + 1,len(final_distributions)):
                r_value, p_value = pearsonr(final_distributions[i], final_distributions[j])
                correlations.append({
                    "cluster_i": i,
                    "cluster_j": j,
                    "pearson_r": r_value,
                    "p_value": p_value
                })

        correlation_df = pd.DataFrame(correlations)
        

        return correlation_df
       
    def create_PCA_ranked_weights(self,outfile_path=None, weights=None, indexes=None):
        '''Create a ranked table of PCA feature weights for the first two principal components.

        Parameters
        ----------

        weights : np.ndarray, shape = (n_components, featuresures)
            PCA component loadings (rows = components, columns = features). If None, this function
            calls `reduce_systems_representations()` to compute PCA (default n=2) and uses the
            returned `weights`.
        indexes : array-like of int
            Residue indices used to label pairwise comparisons. If None, uses `self.indexes`.
            These indices define the order used to generate upper-triangle residue–residue
            comparison labels (e.g., "12-47").

        Returns
        -------
        pandas.DataFrame
            A table mapping each feature (upper-triangle residue pair) to its PCA weights and
            magnitudes. Columns:
                - 'Comparisons'     : str, "i-j" residue pair label
                - 'PC1_Weights'     : float, raw loading for PC1
                - 'PC2_Weights'     : float, raw loading for PC2
                - 'PC1_magnitude'   : float, (PC1_Weights)**2
                - 'PC2_magnitude'   : float, (PC2_Weights)**2
                - 'PC1_mag_norm'    : float, min–max normalized PC1_magnitude to [0,1] (within PC1)
                - 'PC2_mag_norm'    : float, min–max normalized PC2_magnitude to [0,1] (within PC2)

        Notes
        -----
        - Only the upper triangle (excluding the diagonal) of the residue–residue matrix is used,
        so each row corresponds to a unique residue pair.
        - “Weights” are PCA component loadings (eigenvector entries). Squaring gives a magnitude
        that is convenient for ranking feature importance within a component (sign is discarded).
        - The min–max normalization is performed **within each component** to [0,1] and is intended
        for visualization/ranking. Do not compare these normalized values across different PCA
        runs unless you control scaling consistently.
        - This function assumes at least two components are available; it reports PC1 and PC2.

        Examples
        --------
        >>> sa = systems_analysis([traj_array_sys1, traj_array_sys2])
        >>> df = sa.create_PCA_ranked_weights()
        >>> df.head()

        '''

        if weights is None:
            _,weights,_ =self.reduce_systems_representations()
        if weights is not None:
            weights=weights

        outfile_path = outfile_path if outfile_path is not None else os.getcwd()
        indexes=indexes if indexes is not None else self.indexes

        # grab only upper triangle
        triu_idx = np.triu_indices(len(indexes), k=1)

        # Generate comparison labels (no array values needed)
        comparisons = [f"{str(int(indexes[i]))}-{str(int(indexes[j]))}" for i, j in zip(*triu_idx)]
        dataframe={
            'Comparisons':comparisons,
            'PC1_Weights':weights[0],
            'PC2_Weights':weights[1],
            'PC1_magnitude':weights[0]**2,
            'PC2_magnitude':weights[1]**2,
        
        }

        dataframe=pd.DataFrame(dataframe).round(3)
        
        return dataframe

 
    #Algorithm wrappers 
    def preform_clust_opt(self,outfile_path, max_clusters=None, data=None):
        '''
        Parameters
        ----------
        data:np.ndarray,shape=(n_sample,featuresures),
            A feature matrix of any kind, hopefully one provided from the rest of the pipeline but in theory, this is 
            just a scikit learn wrapper so you can plug anything you want really
        
        outfile_path:str,default=os.getcwd()
        

        Returns
        ----------
        
        Notes
        ----------
        
        Examples
        ----------
        
        '''
        data = data if data is not None else self.feature_matrix
        outfile_path = outfile_path if outfile_path is not None else os.getcwd()
        max_clusters = max_clusters if max_clusters is not None else 10
        
        
        #keeping track of our scores 
        inertia_scores,silhouette_scores,all_labels,centers = [],[],[],[]
        cluster_range = range(2, max_clusters+1)


        for k in cluster_range:
            kmeans = KMeans(n_clusters=k, init='random', n_init=k, random_state=0) #we set
            kmeans.fit(data) #fit data and now we have everything transformed
            cluster_centers, inertia, cluster_labels = kmeans.cluster_centers_,kmeans.inertia_,kmeans.labels_
            sil_score = silhouette_score(data, cluster_labels)
            
            centers.append(cluster_centers)
            inertia_scores.append(inertia)
            silhouette_scores.append(sil_score)
            all_labels.append(cluster_labels)


            np.save(f"{outfile_path}kluster_labels_{k}clust",cluster_labels)

        
        #so we save unless your calling this specific optimization
        from mdsa_tools.Viz import plot_elbow_scores,plot_sillohette_scores

        
        optimal_sillohuette=plot_sillohette_scores(cluster_range,silhouette_scores,outfile_path)
        optimal_elbow=plot_elbow_scores(cluster_range,inertia_scores,outfile_path)

        #print(f"\nsize of labels:{len(all_labels)} ,optimal_elbow: {optimal_elbow}:optimal_sillohuette {optimal_sillohuette}")

        # Now you can return optimal k values
        
        optimal_k_silhouette_labels = all_labels[optimal_sillohuette-2] 
        optimal_k_elbow_labels = all_labels[optimal_elbow-2]
        centers_sillohuette = centers[optimal_sillohuette-2] 
        centers_elbow = centers[optimal_elbow-2] 

        
        return optimal_k_silhouette_labels,optimal_k_elbow_labels,centers_sillohuette,centers_elbow
    
    def run_PCA(self,feature_matrix,n):
        '''small function for running principal components analysis

        Parameters
        ----------

        feature_matrix:np.ndarray,shape=(sum(n_frames),n_residues*n_residues) where the sum of n_frames refers to the total number of frames.
            Each row of the new matrix represents a flattened adjacency matrix for each frame, and the frames are stacked
            in such a way that each of the original arrays follow each other sequentially.
        
        n:int,default=2
            The number of principal components you would like to reduce your dataset down to

        Returns
        -------




        Notes
        -----




        Examples
        --------



        '''

        pca=PCA(n_components=n)
        pca.fit(feature_matrix)
        X_pca = pca.transform(feature_matrix)
        weights = pca.components_
        explained_variances = pca.explained_variance_ratio_

        print("X_pca shape (new data):",X_pca.shape)
        print(f"the total explained variance{np.sum(explained_variances)}")
        print(f"the total explained variance of PC's is {explained_variances}")
        print("weights shape:", weights.shape) 
        
        return X_pca,weights,explained_variances



if __name__ == '__main__':

    print('testing testing 1 2 3')



