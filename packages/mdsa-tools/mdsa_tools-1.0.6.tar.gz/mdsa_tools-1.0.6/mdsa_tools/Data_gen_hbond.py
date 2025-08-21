import numpy as np
import mdtraj as md
from typing import Tuple, Dict

class TrajectoryProcessor():
    '''A wrapper class for creating and manipulating systems representations of our trajectories
    
    '''

    def __init__(self, trajectory_path,topology_path):
        '''
        Parameters
        ----------

        Trajectory_path:str,
            A path to a trajectory
        
        Topology_path:str,
            A path to the topology pertaining to the trajectory youd like to load
        
        Returns
        -------
        Nothing this is an init


        Examples
        --------


        Notes
        -----
        The clause is really just to distinguish between formats that inherently carry topology information (PDBs for example)
        and cases where you have to load it in yourself (mdcrd+prmtop for example).

        '''
        #load in parameters
        if topology_path is not None:
            self.trajectory=md.load(trajectory_path,top=topology_path)
        elif topology_path is None:
            self.trajectory=md.load(trajectory_path)
        
        # setup empty system representation
        # could be done later but I find the explicit definition is more readable
        self.system_representation=None 
        self.filtered_representation=None
        self.feature_matrix=None
        self.topology = self.trajectory.topology

    def create_filtered_representations(self,residues_to_keep,systems_representation=None):
        '''Filters arrray representations to contain only residues of interest

        Parameters
        ----------

        systems_representation: np.ndarray, shape=(n_frames,n_residues,n_residues)
            Array containing adjacency matrices for every frame. Shape is dependent on residues in trajectory and number of frames.
        
        res_of_interest: 
            An array containing residues of interest 


        Examples
        --------



        Notes
        -----

        
        '''
        if systems_representation is not None:
            systems_representation=systems_representation
        if self.system_representation is not None:
            systems_representation=self.system_representation
        if self.system_representation is None:
            self.create_system_representations()
            systems_representation=self.system_representation

       
       

        residues_to_keep = [0]+residues_to_keep 
        if len(systems_representation.shape)==2:

            # Create a mask that marks the rows and columns to keep
            row_mask = np.isin(systems_representation[:, 0], residues_to_keep)
            col_mask = np.isin(systems_representation[0, :], residues_to_keep)

            filtered_rows=systems_representation[row_mask,:]
            filtered_array=filtered_rows[:,col_mask]
            
            
        #3dimensional filtering
        elif len(systems_representation.shape)==3:

            filtered_array=[]

            for i in range(systems_representation.shape[0]):

                current_frame = systems_representation[i,:,:]

                if len(current_frame.shape)==2:

                    row_mask = np.isin(current_frame[:, 0], residues_to_keep)
                    col_mask = np.isin(current_frame[0, :], residues_to_keep)

                    filtered_rows=current_frame[row_mask,:]
                    filtered_frame=filtered_rows[:,col_mask]
                    filtered_array.append(filtered_frame)

                elif len(current_frame.shape)!=2:
                    print("frame not correctly indexed")
                    break
                
        filtered_array=np.array(filtered_array)
        self.filtered_representation=filtered_array

        return filtered_array

    def create_system_representations(self,trajectory=None,granularity=None):
        '''Wraps operations for creating systems representations into a nice single method

        Parameters
        ----------
        trajectory:mdtraj.Trajectory:
            An mdtraj trajectory object that should have in theory been created when you load in the class but, can also be included in the
            argument

        Returns
        -------
        
        Systems: np.ndarray, shape=(n_frames,n_residues,n_residues)
            returns array containing adjacency matrices for every frame. Shape is dependent on residues in trajectory and number of frames.

        Examples
        --------
        >>> 
        >>>
        >>>

        '''
        granularity = granularity if granularity is not None else 'residue'
        trajectory = trajectory if trajectory is not None else self.trajectory

        if granularity == 'residue':
            atom_to_residue,template_array = self.create_attributes(trajectory)
            trajectory_array = self.Process_trajectory(trajectory=self.trajectory,array_template=template_array,atom_to_residue=atom_to_residue)
            self.system_representation=trajectory_array
        if granularity == 'atom':
            template_array = self.create_attributes(trajectory,granularity='atom')
            trajectory_array = self.Process_trajectory(trajectory=self.trajectory,array_template=template_array,granularity='atom')
       
        return trajectory_array 

    def create_attributes(self, trajectory,granularity=None) -> Tuple[np.ndarray, Dict]:
        '''returns atom to residue dictionary and template array for processing

        Parameters
        ----------
        trajectory:mdtraj.Trajectory

        Returns
        -------
        atom_to_residue:Dict, atom_to_residue[atom_index]=residue_index
            Dictionary containing atom to residue mappings

        template_array: np.ndarray, shape=(n_frames,n_residues,n_residues)
            returns array containing adjacency matrices for every frame. Shape is dependent on residues in trajectory and number of frames.

        Examples
        --------
        

        Notes
        -----
        This atom to residue dictionary is important as the function we will use for extracting hydrogen bonding information
        returns hydrogen bonds at the atomic level, and we need it at the residue level for this particular "systems" 
        representation. 

        The template array is so we only create one datastructure to modify later improving efficiency.

        '''

        granularity = granularity if granularity is not None else 'residue'

        #Make atom to residue dictionary 

        #Create adjacency matrix, set first row and column as residue indices, and multiply to match the number of frames
        
        trajectory = trajectory if trajectory is not None else self.trajectory

        if granularity == 'residue':
            indexes=[residue.resSeq+1 for residue in trajectory.topology.residues]
            empty_array = np.zeros(shape=(len(indexes)+1,len(indexes)+1)) 

            empty_array[0,1:]=indexes
            empty_array[1:,0]=indexes

            template_array=np.repeat(empty_array[np.newaxis,:, :], len(trajectory), axis=0)
            atom_to_residue = {atom.index:atom.residue.resSeq for atom in trajectory.topology.atoms}
            
            return atom_to_residue,template_array
        
        elif granularity == 'atom':
            indexes=[atom.index+1 for atom in trajectory.topology.atoms]
            empty_array = np.zeros(shape=(len(indexes)+1,len(indexes)+1)) 

            empty_array[0,1:]=indexes
            empty_array[1:,0]=indexes

            template_array=np.repeat(empty_array[np.newaxis,:, :], len(trajectory), axis=0)
            return template_array

    def Process_trajectory(self,trajectory,array_template,atom_to_residue=None,granularity=None)->np.ndarray:
            """returns a call to the now modified array template which has been filled in with data
            
            Processes an individual frame of template array and fills in hydrogen bonding values.
            
            Parameters
            ----------
            trajectory:md.trajectory

            array_template:np.ndarray,shape=(n_residues,n_residues,n_frames)
                This is an empty array of shape (n_residues,n_residues,n_frames) where we have
                n_frames worth of adjacency matrices of size n_residues*n_residues
            
            atom_to_residue:Dict, Dict[atom_index]=residue_index
                Dictionary containing atom to residue index mappings      

            frame:int
                Integer for indexing what frame we are iterating over in array        

                
            Returns
            -------
            array_template:np.ndarray,shape=(n_frames,n_residues,n_residues)
                A reference to the original array. It is updating the same array in memory but, in theory
                it is done for throughness.



            Examples
            --------



            Notes
            -----
        


            """
            granularity = granularity if granularity is not None else 'residue'
            atom_to_residue = atom_to_residue if atom_to_residue is not None else None

            for frame in range(0,len(trajectory)):
                #splice our current frame and use axis for indexing
                current_frame=array_template[frame]
                
                #Use Baker Hubard to get donor and acceptor atom indexes then map to residue indexes
                Baker_hubbard=md.baker_hubbard(trajectory[frame])
                donor_atoms,acceptor_atoms=Baker_hubbard[:,0],Baker_hubbard[:,2]


                #adding a cluse in here so this is for exploring at the residue level
                if granularity == 'residue':
                    donor_residues,acceptor_residues=np.array([atom_to_residue[atom] for atom in donor_atoms]),np.array([atom_to_residue[atom] for atom in acceptor_atoms])

                    #match atoms to residues and increment in array
                    for i in range(donor_residues.shape[0]):
                        current_donor,current_acceptor=donor_residues[i]+1,acceptor_residues[i]+1
                        if current_donor != current_acceptor:
                            current_frame[current_donor, current_acceptor] += 1
                            current_frame[current_acceptor, current_donor] += 1

                # this is for exploring at the atomic level
                elif granularity == 'atom':
                    for i in range(donor_atoms.shape[0]):
                        current_donor,current_acceptor=donor_atoms[i]+1,acceptor_atoms[i]+1
                        if current_donor != current_acceptor:
                            current_frame[current_donor, current_acceptor] += 1
                            current_frame[current_acceptor, current_donor] += 1

            return array_template

class cpptraj_hbond_import():

    def __init__(self,filepath,topology):
        ''' Init takes just the filepath to the desires data and then the topology

        Parameters
        ----------



        Returns
        -------



        Examples
        --------



        Notes
        -----



        '''
        self.indices=self.extract_headers(filepath)
        self.data=np.loadtxt(filepath, skiprows=1, usecols=range(1, len(self.indices)+1), dtype=int)
        self.topology = md.load_topology(topology) 

        return
     
    def extract_headers(self,filepath):
        '''Smaller module for importing files from cpptraj 

        Parameters
        ----------



        Returns
        -------



        Notes
        -----



        Examples
        --------


        '''
        filepath = filepath if filepath is not None else None

        lines=[]
        indices=[]
        with open(filepath,'r') as infile:
            for line in infile:
                lines.append(line.split())

        for col_header in lines[0]:
            if col_header !='#Frame':
                res1 = col_header.split('_')[1].split('@')[0]
                res2 = col_header.split('_')[2].split('@')[0]
                indices.append((int(res1),int(res2)))
        return indices

    def create_cpptraj_attributes(self,data,topology,granularity=None):
            '''returns atom to residue dictionary and template array for processing

            Parameters
            ----------
            trajectory:mdtraj.Trajectory

            Returns
            -------
            atom_to_residue:Dict, atom_to_residue[atom_index]=residue_index
                Dictionary containing atom to residue mappings

            template_array: np.ndarray, shape=(n_frames,n_residues,n_residues)
                returns array containing adjacency matrices for every frame. Shape is dependent on residues in trajectory and number of frames.

            Examples
            --------
            

            Notes
            -----
            This atom to residue dictionary is important as the function we will use for extracting hydrogen bonding information
            returns hydrogen bonds at the atomic level, and we need it at the residue level for this particular "systems" 
            representation. 

            The template array is so we only create one datastructure to modify later improving efficiency.

            '''

            granularity = granularity if granularity is not None else 'residue'

            #Make atom to residue dictionary 

            #Create adjacency matrix, set first row and column as residue indices, and multiply to match the number of frames
            
            topology = md.load_topology(topology) if topology is not None else self.topology

            if granularity == 'residue':

                indexes=[residue.resSeq+1 for residue in topology.residues]
                empty_array = np.zeros(shape=(len(indexes)+1,len(indexes)+1)) 

                empty_array[0,1:]=indexes
                empty_array[1:,0]=indexes

                template_array=np.repeat(empty_array[np.newaxis,:, :], data.shape[0], axis=0)

                return template_array
            
    def create_systems_rep(self,data=None,topology=None,indices=None):
        '''Filling in the matrix

        Parameters
        ----------

        Returns
        -------

        Notes
        -----

        Examples
        --------

        '''
        topology = topology if topology is not None else self.topology
        data = data if data is not None else self.data
        indices = indices if indices is not None else self.indices

        template_array=self.create_cpptraj_attributes(data,topology)

        iterator=0

        for col in data.T: #simply transpose so we are going column wise instead
            current_pair=indices[iterator]

            if current_pair[0]!=current_pair[1]:
                template_array[:,current_pair[0]-1,current_pair[1]-1]=col

            iterator+=1
        
        return template_array
    

if __name__ == '__main__':

    #load in and test trajectory
    topology = '/Users/luis/Desktop/workspace/PDBs/5JUP_N2_GCU_nowat.prmtop'
    traj = '/Users/luis/Desktop/workspace/PDBs/CCU_GCU_10frames.mdcrd' 
    test_trajectory = trajectory(trajectory_path=traj,topology_path=topology)
    test_atomic_system=test_trajectory.create_system_representations(test_trajectory.trajectory,granularity='atom')
    print(test_atomic_system.shape)

    test_atomic_system_no_indexes=test_atomic_system[0,1:,1:]
    print(test_atomic_system_no_indexes[test_atomic_system_no_indexes!=0])

    print('test running just the datagen file')
    