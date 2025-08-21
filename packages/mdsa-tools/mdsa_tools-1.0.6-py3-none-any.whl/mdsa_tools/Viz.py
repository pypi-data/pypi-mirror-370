import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import pycircos.pycircos as py 
import seaborn as sns



#Replicate maps
def replicatemap_from_labels(labels,frame_list,savepath=None,title=None,
                              xlabel=None, ylabel=None,
                             cbar_label=None,
                             cmap=None) -> np.ndarray:
    '''returns an array consisting of a re-formatted list of labels through which to view a set.

    Parameters
    ----------
    labels: listlike,shape=(data,)
        A list of labels representing all of the labels from either a Kmeans or other analysis that we would like to
        use for our analysis.

    frame_list: listlike,shape=(data,)
        A list of integers representing the number of frames present in each replicate. This should be in the order
        of which the various versions of the system, and replicates where concatenated. 

    savepath:str,default=os.getcwd()
        Path to where you would like to save your plot; generally dpi=800 and default is the directory you are running from

    title : str, default = None
        Optional title for the plot.

    xlabel : str, default = None
        Optional label for the x-axis.

    ylabel : str, default = None
        Optional label for the y-axis.

    Returns
    -------
    reformatted_labels:numpy.ndarray,shape=(n_replicates,n_frames)
        A final array is returned where each row corresponds to one of our replicates in simulations.
        Each column corresponds to that particular frame in the replicate. If there are replicates of varying lengths
        we pad all to the longest trajectorys length with masked nans.

        
    Examples
    -------- 
    

    Notes
    -----
    

    '''
    cmap=cmap if cmap is not None else cm.magma_r

    savepath=savepath if savepath is not None else os.getcwd()


    iterator=0
    final_coordinates=[]

    for i in range(len(frame_list)):
        current_replicate_coordinates=np.full(shape=(frame_list[i],),fill_value=i) #make list of 11111 then 22222 for each rep
        frame_positions=np.arange(1,frame_list[i])
        frame_values=labels[iterator:iterator+frame_list[i]]
        replicate_block = np.stack([current_replicate_coordinates, frame_positions, frame_values], axis=1)
        final_coordinates.append(replicate_block)
        iterator+=frame_list[i]
    
    final_coordinates = np.vstack(final_coordinates)

    y_spacing_factor = 1
    x_spacing_factor = 1

    scatter=plt.scatter(
                x=final_coordinates[:,1] * x_spacing_factor,
                y=final_coordinates[:,0] * y_spacing_factor,
                c=final_coordinates[:,2],
                s=1,
                marker='s',
                cmap=cmap)
    
    #cbar and cbar ticks
    cbar = plt.colorbar(scatter, ax=plt.gca(), shrink=0.8, pad=0.02)
    cbar.set_label(cbar_label if cbar_label is not None else 'Value', fontsize=10)
    unique_vals = np.unique(final_coordinates[:, 2])
    cbar.set_ticks(unique_vals)
    cbar.set_ticklabels([str(int(u)) for u in unique_vals])

    #personal preferences
    plt.grid(visible=False)
    currentaax=plt.gca()
    for spine in currentaax.spines.values():
        spine.set_visible(False)

    ax=plt.gca()
    ax.invert_yaxis()
    ax.set_title('Clusters per frame', fontsize=20, weight='bold', family='monospace', style='italic')
    n_reps = int(final_coordinates[:, 0].max())
    n_frames = int(final_coordinates[:, 1].max())

    #Setting Ticks
    x_ticks_labels = np.arange(0, n_frames,10) 
    x_ticks_locations = x_ticks_labels * x_spacing_factor
    ax.set_xticks(x_ticks_locations)
    ax.set_xticklabels([str(i) for i in x_ticks_labels],fontsize=8)


    y_ticks_labels = np.arange(0,final_coordinates.shape[0],final_coordinates.shape[0]/10) if final_coordinates.shape[0] else np.arange(0, 2, 1)
    y_ticks_locations = y_ticks_labels * y_spacing_factor
    ax.set_yticks(y_ticks_locations)
    ax.set_yticklabels([str(i) for i in y_ticks_labels], fontsize=8)

    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)



    plt.tight_layout()
    plt.savefig(f'{savepath}replicate_map.png', dpi=800)
    plt.close()

    return 

#K-means Cross-validation metrics
def plot_sillohette_scores(cluster_range, silhouette_scores, outfile_path="sillohette_method.png",
                           title=None, xlabel=None, ylabel=None):
    """
    Plot silhouette scores over k and mark the maximum.

    Parameters
    ----------
    cluster_range : array-like
        k values evaluated.

    silhouette_scores : array-like
        Silhouette score per k.

    outfile_path : str, default="sillohette_method.png"
        Path prefix where figure is saved (suffix 'sillohuette_plot' is appended).

    title, xlabel, ylabel : str or None
        Optional title/axis labels.

    Returns
    -------
    optimal_k_sil : int
        k with max silhouette score.
    """
    optimal_k_sil = cluster_range[np.argmax(silhouette_scores)]#return index 
    # Plot Silhouette Scores
    plt.figure(figsize=(8, 5))
    plt.plot(cluster_range, silhouette_scores, marker='o', linestyle='-')
    plt.axvline(optimal_k_sil, color='red', linestyle='--', linewidth=2, label=f'Optimal k = {optimal_k_sil}')

    plt.xlabel(xlabel if xlabel is not None else 'Number of Clusters (k)')
    plt.ylabel(ylabel if ylabel is not None else 'Silhouette Score')
    plt.title(title if title is not None else 'Silhouette Score for optimal K')
    plt.legend()
    plt.grid(True)
    plt.savefig(outfile_path + 'sillohuette_plot', dpi=300)
    plt.close()
    return optimal_k_sil

def plot_elbow_scores(cluster_range, inertia_scores, outfile_path="elbow_method.png",
                      title=None, xlabel=None, ylabel=None):
    """
    Plot inertia over k and mark elbow via second derivative.

    Parameters
    ----------
    cluster_range : array-like
        k values evaluated.

    inertia_scores : array-like
        KMeans inertia per k.

    outfile_path : str, default="elbow_method.png"
        Path prefix where figure is saved (suffix 'elbow_plot' is appended).

    title, xlabel, ylabel : str or None
        Optional title/axis labels.

    Returns
    -------
    optimal_k : int
        Estimated elbow k.
    """
    diff = np.diff(inertia_scores)
    diff2 = np.diff(diff)
    optimal_k = cluster_range[np.argmin(diff2) + 1]

    plt.figure(figsize=(8, 5))
    plt.plot(cluster_range, inertia_scores, marker='o', linestyle='-')
    plt.axvline(optimal_k, color='red', linestyle='--', linewidth=2, label=f'Optimal k = {optimal_k}')

    plt.xlabel(xlabel if xlabel is not None else 'Number of Clusters (k)')
    plt.ylabel(ylabel if ylabel is not None else 'Inertia (Sum of Squared Distances)')
    plt.title(title if title is not None else 'Elbow Method for Optimal k')
    plt.legend()
    plt.grid(True)
    plt.savefig(outfile_path + 'elbow_plot', dpi=300)
    plt.close()

    return optimal_k

#Circos plots
def get_Circos_coordinates(residue, gcircle):
    """helper function for creating coordinates for arc sizes in Circos graph

    Parameters
    ----------
    residue:int,default=None
        A residue index from which to create the current arc (in general you will be iterating
        through residue indexes when using this method)

    gcirlce:py.Gcircle,default=py.Gcircle(figsize=(6,6))
        A Pycircos Gcricle object. By default we use one with a figsize of (6,6).

    

    Return a 4-element tuple telling PyCircos chord_plot()
    to start in the middle of the arc with a radial anchor of 550.



    Returns
    -------
    tuple:coordinates:defualt=(residue, mid_position, mid_position, raxis_position)
        A four member tuple consisting of the positioning needed to create an arc.



    Notes
    -----




    Examples
    --------


    
    """
    arc = gcircle._garc_dict[residue]
    # The "size" is the arc length in PyCircos coordinates
    mid_position = arc.size * 0.5  # center of the arc
    # We'll anchor all chords at radial = 550
    # (this can be changed if your arcs are drawn in a different radial band)
    raxis_position = 550
    return (residue, mid_position, mid_position, raxis_position)

def make_MDCircos_object(residue_indexes):
    """Returns a PyCircos Gcircle scaled arcs

    Returns a PyCircos Gcircle object whose arcs are automatically scaled
    based on how many arcs (residues) there are. Also scales line widths,
    so that very few arcs don't produce huge lines and many arcs don't
    produce lines too thin to see.

    Parameters
    ----------
    residue_indexes : list
        List of residue indices you want as arcs.

    Returns
    -------
    circle : py.Gcircle
        A PyCircos object containing arcs scaled by the number of residues.
    """

    if len(residue_indexes) <= 50:
        circle = py.Gcircle(figsize=(6, 6))
        plt.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)

        # Add each arc
        for index in residue_indexes:
            circle.add_garc(
                py.Garc(
                    arc_id=str(index),
                    facecolor='#FFFFFF',   
                    edgecolor='#000000',   
                    label=str(index),
                    label_visible=True,
                    labelposition=40,
                    labelsize=6,
                    size=10,        
                    interspace=0,          
                    linewidth=.1          
                )
            )

        circle.set_garcs()


    if len(residue_indexes) >50:
        circle = py.Gcircle(figsize=(10, 10))
        plt.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)

        # Add each arc
        for index in residue_indexes:
            circle.add_garc(
                py.Garc(
                    arc_id=str(index),
                    facecolor='#FFFFFF',   # White arcs
                    edgecolor='#000000',   # Black outline
                    label=str(index),
                    label_visible=True,
                    labelposition=30,
                    labelsize=2,
                    size=100,         # scaled by number of arcs
                    interspace=4,          # small gap
                    linewidth=.1           # scaled line thickness
                )
            )

    circle.set_garcs()
    return circle

def mdcircos_graph(empty_circle, residue_dict, savepath=os.getcwd()+'mdcircos_graph', scale_factor=5,colormap=cm.magma_r):
    ''' creates and saves a mdcircos graph to a desired output directory

    Parameters
    ----------
    Residue_indexes:list, shape=(n_residues)
        A list of residue indexes pertaining to the residues you would like to use as parts of the circle

    Residue_dict:dict,format:dict['residue']=float(value)
        A dictionary where keys are residue indexes (as strings) and values are floats representing the corresponding 
        edge weights in the adjacency matrix (or another method) used for mapping.

    savepath:str(),default=os.getcwd()+'mdcircos_graph'
        Absolute path to the location and name of the file you would like to save the file. Default is mdcircos_graph in the 
        working directory

    Residue_dict:dict,dict['residue']=float(value)
        A dictionary containing mappings from specific residue indexes *as strings* to their respective edge weights in whatever adjacency matrix
        (or other method) is being used as the basis for mapping.
    
    scale_values:bool,default=False
        A boolean argument meant to give the user the option of using a gradient color map in order to visualize stronger interactions

    Returns
    -------
    None
        Strictly a graphing function the methods can be called individually if youd like to tamper with the
        Circos object further


    Notes
    -----
    This is built as basically a wrapper for another python package so it is a little finicky in its implementation. In theory it should work fine
    with the other two functions and really only needs to be specific in the way that its taking the inputs for.
    
    An important note is that the scale is saved as a seperate colorbar and the values are normalized by min max because it takes
    generally as input the weightings which happen to be too small to really visualize well typically.

    
    Examples
    --------

    '''
   
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.colors import Normalize
    import numpy as np


    # Normalize the colors based on the values provided 
    vals = list(residue_dict.values())
    vmin, vmax = min(vals), max(vals)
    color_norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = colormap if colormap is not None else cm.plasma
    hex_color_map = {k: cmap(color_norm(v)) for k, v in residue_dict.items()}

    # Width normalization on the absolute values via min–max (makes plot aesthetically closer to raw
    # values it is still suggested to use outputted tables for any actual raw analysis of values)
    abs_vals = [abs(v) for v in vals if v != 0]
    min_abs, max_abs = min(abs_vals), max(abs_vals)

    # avoid division by zero if all values are the same magnitude
    denom = max_abs - min_abs if max_abs != min_abs else 1.0

    width_norm = {
        k: (abs(v) - min_abs) / denom
        for k, v in residue_dict.items()
    }

    # 3) Plot chords
    for key, value in residue_dict.items():
        if value == 0:
            continue
        
        res1, res2 = key.split('-')
        arc1 = get_Circos_coordinates(res1, empty_circle)
        arc2 = get_Circos_coordinates(res2, empty_circle)
        color = hex_color_map[key]

        lw = width_norm[key] * scale_factor
        empty_circle.chord_plot(arc1, arc2,
                                linewidth=lw,
                                facecolor=color,
                                edgecolor=color)

    empty_circle.figure.savefig(savepath + ".png",
                                dpi=300, bbox_inches="tight")

    # 4) Separate colorbar (using the original signed range)
    fig_cb, ax_cb = plt.subplots(figsize=(1.5, 4))
    sm = cm.ScalarMappable(cmap=cmap, norm=color_norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, cax=ax_cb)
    ticks = np.linspace(vmin, vmax, num=6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{t:.2f}" for t in ticks])
    cbar.set_label("Directional Difference")

    fig_cb.savefig(savepath + "_colorbar.png",
                dpi=300, bbox_inches="tight")
    
    plt.close(fig_cb)

def extract_properties_from_weightsdf(pca_table):

    comps = pca_table['Comparisons'].astype(str)

    # split stack and clean
    sides = comps.str.split('-', n=1, expand=True)
    residues = (sides.stack()
                      .str.strip()
                      .dropna()
                      .unique())

    # arc ids are strings
    residues = [str(x) for x in residues]

    PC1_weight_dict = pca_table.set_index('Comparisons')['PC1_magnitude'].to_dict()
    PC2_weight_dict = pca_table.set_index('Comparisons')['PC2_magnitude'].to_dict()
    return residues, PC1_weight_dict, PC2_weight_dict

def create_MDcircos_from_weightsdf(PCA_ranked_weights, outfilepath=None):
    '''Processes Weights table to create MDcircos plots visualizing weightings

    Parameters
    ----------
    PCA_ranked_weights:Pandas.DataFrame,default=None
      A table containing the ranked weights we created as a part of the analysis Systems Analysis
      module. It is expected that it wold contain columns with the headers:

    Returns
    -------
    None

    Notes
    -----
    Mdcircos plots where arcs are residue indexes and line thickness and darkness are eigenvector coefficient magnituses. 



    Examples
    --------



    Notes
    -----


    '''
    outfilepath = outfilepath if outfilepath is not None else os.getcwd()

    res_indexes,PC1_magnitude_dict,PC2_magnitude_dict = extract_properties_from_weightsdf(PCA_ranked_weights)
    pc1_circos_object=make_MDCircos_object(res_indexes)
    pc2_circos_object=make_MDCircos_object(res_indexes)
    mdcircos_graph(pc1_circos_object,PC1_magnitude_dict,outfilepath+'PC1_magnitudeviz')
    mdcircos_graph(pc2_circos_object,PC2_magnitude_dict,outfilepath+'PC2_magnitudeviz') 

#Embeddingspace visualizations
def create_2d_color_mappings(labels=([80]*20)+([160]*10), 
                             colors_list=['purple', 'orange', 'green', 'yellow', 'blue', 'red', 'pink', 'cyan', 'grey', 'brown'], 
                             clustering=True):
    ''' 
    Parameters
    ----------
    labels: list, shape (n_samples), default=([80]*20)+([160]*10)
        A list of integers that help describe how you want to label each sample once they have been reduced to 2 dimensions.

    colors_list: list-like, default=['purple', 'orange', 'green', 'yellow', 'blue', 'red', 'pink', 'cyan', 'grey', 'brown']
        A list of colors that we can use to visualize all of our clusters.

    clustering: bool, default=True
        Whether to assign discrete colors for clusters (True) or use a heatmap-based visualization (False).
    '''

    if clustering == True:
        # Create a dictionary mapping each label to a color
        label_dict = {}
        i = 0
        for label in labels:
            if label not in label_dict:
                label_dict[label] = colors_list[i % len(colors_list)]  # Ensure cycling through colors if necessary
                i += 1
        sample_color_mappings = [label_dict[i] for i in labels]
        return sample_color_mappings

def visualize_reduction(embedding_coordinates, color_mappings=None, 
                  custom=False, 
                  savepath=os.getcwd(), 
                  title=None, 
                  colors_list=['purple', 'orange', 'green', 'yellow', 'blue', 'red', 'pink', 'cyan', 'grey','brown'],
                  cmap=None,
                  legend_labels=None,
                  axis_one_label=None,
                  axis_two_label=None,
                  cbar_label=None):

    axis_one_label=None if axis_one_label is not None else 'Embedding Space Axis 1'
    axis_two_label=None if axis_two_label is not None else 'Embedding Space Axis 2'
    title=title if title is not None else "Dimensional Reduction of (PCA) of GCU and CGU Systems"
    cbar_label=cbar_label if cbar_label is not None else "Value"

    labels_font_dict = {
        'family': 'monospace',
        'size': 20,
        'weight': 'bold',
        'style': 'italic',
        'color': 'black',
    }

    fig = plt.figure(figsize=(16, 12), dpi=300)
    ax = plt.gca()

    if color_mappings is None or len(color_mappings) == 0:
        color_mappings = np.arange(embedding_coordinates.shape[0])
        custom = False
        legend_labels = None
        print("No color_mappings provided — defaulting to sample index gradient.")
    
    unique_vals = np.unique(color_mappings)
    
    if custom:
        # Discrete category color mapping
        scatter = ax.scatter(embedding_coordinates[:, 0], embedding_coordinates[:, 1], c=color_mappings, 
                             cmap=ListedColormap(colors_list[:len(unique_vals)]), alpha=0.6)
        
        if legend_labels is not None:
            legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markersize=10, 
                                         markerfacecolor=color, label=label) 
                              for label, color in legend_labels.items()]
            ax.legend(handles=legend_handles, title="System Types", loc="upper right", prop={'size': 20, 'weight': 'bold'})

    else:
        # Use provided colormap, fallback to red
        norm = Normalize(vmin=np.min(color_mappings), vmax=np.max(color_mappings))
        cmap = cmap if cmap is not None else plt.get_cmap('Reds')

        ax.scatter(embedding_coordinates[:, 0], embedding_coordinates[:, 1],
                             c=color_mappings, cmap=cmap, norm=norm, alpha=0.6)

        cbar_ticks = np.linspace(np.min(color_mappings), np.max(color_mappings), 10, dtype=int)
        
        cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                            ticks=cbar_ticks, shrink=0.8, aspect=30, pad=0.02)
        
        cbar.set_label(cbar_label, fontdict=labels_font_dict,
                       rotation=270, labelpad=25)
        
        cbar.ax.set_yticklabels([str(t) for t in cbar_ticks])

    # Final touches
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(title, fontdict=labels_font_dict)
    ax.set_xlabel(axis_one_label, fontdict=labels_font_dict)
    ax.set_ylabel(axis_two_label, fontdict=labels_font_dict)
    ax.tick_params(axis='x', colors='black')  
    ax.tick_params(axis='y', colors='black')

    plt.tight_layout()
    plt.savefig(savepath, dpi=500)
    plt.close()

def visualize_candidate_states(candidate_states,reduced_coordinates,savepath=None,cmap=None):
    '''visualize the candidate states discovered by clustering embedding space

    Parameters
    ----------
    candidatestates=arraylike,default=mdsa_tools.Analysis.cluster_embeddingspace(),shape=(number_of_systems_)
        A list of arrays holding, each array in every system contains the cluster assignments and labels returned
        from the system analysis module's preform_clust_opt() operation.
    
    Reduced_cooridinates:

    cmap:
        cmap
    
    '''
    savepath=savepath if savepath is not None else os.getcwd()
    frames_per_sys=np.array_split(reduced_coordinates,len(candidate_states))

    
    for i in range(len(candidate_states)):
        labels,_ = candidate_states[i][0],candidate_states[i][1]
        from mdsa_tools.Viz import visualize_reduction
        visualize_reduction(frames_per_sys[i],cmap=cmap,color_mappings=labels,savepath=f'{savepath}/system_{i}')


    return
    
def highlight_reps_in_embeddingspace(reduced_coordinates,
                    frame_list=((([80] * 20) + ([160] * 10)) * 2),
                    outfilepath='/zfshomes/lperez/thesis_figures/PCA/test_one_rep',
                    cmap=cm.magma_r):
    '''Visualizes and saves a replicates inside of embedding space

    Parameters
    ----------
    X_pca : np.ndarray, shape=(n_samples, n_components)
        The results of fitting a PCA analysis and using the .transform() method.

    frame_list : list of int, optional
        A list holding integer counts of the number of frames in each replicate. 
        Default is (([80] * 20) + ([160] * 10)) * 2.
    
    cmap:matplotlib.cm.cmap:,default=magma_r
        colormap of choice for highlighting replicates in embeddingspace

    Returns
    -------
    None

    Notes
    -----
    Each replicate is plotted in its own subplot. A new row of plots begins every 30 replicates.
    '''

    rep_iterator = 0
    
    for entry in range(len(frame_list)):
        
        colors = np.full(shape=reduced_coordinates.shape[0],fill_value=0)
        colors[rep_iterator:rep_iterator+frame_list[entry]] = np.arange(1,frame_list[entry]+1,1) 

        # ticks for scaling
        x_min, x_max = reduced_coordinates[:, 0].min(), reduced_coordinates[:, 0].max()
        y_min, y_max = reduced_coordinates[:, 1].min(), reduced_coordinates[:, 1].max()
        plt.xticks(np.arange(np.floor(x_min), np.ceil(x_max) + 1, 1))
        plt.yticks(np.arange(np.floor(y_min), np.ceil(y_max) + 1, 1))

        plt.scatter(reduced_coordinates[:,0],reduced_coordinates[:,1],c=colors,s=5,cmap=cmap)
        plt.grid(visible=False)
        plt.savefig(f"{outfilepath}_rep{entry}.png")
        plt.close()
        
        rep_iterator+=frame_list[entry]
    
    return

def highlight_crawl_directions(reduced_coordinates,
                    frame_list=((([80] * 20) + ([160] * 10)) * 2),
                    outfilepath='/zfshomes/lperez/thesis_figures/PCA/test_one_rep',
                    cmap=cm.magma_r):
    '''Visualizes and saves a replicates inside of embedding space

    Parameters
    ----------
    X_pca : np.ndarray, shape=(n_samples, n_components)
        The results of fitting a PCA analysis and using the .transform() method.

    frame_list : list of int, optional
        A list holding integer counts of the number of frames in each replicate. 
        Default is (([80] * 20) + ([160] * 10)) * 2.
    
    cmap:matplotlib.cm.cmap:,default=magma_r
        colormap of choice for highlighting replicates in embeddingspace

    Returns
    -------
    None

    Notes
    -----
    Each replicate is plotted in its own subplot. A new row of plots begins every 30 replicates.
    '''

    colormappings=[np.arange(0,np.max(i),1) for i in frame_list]
    colormappings=np.concatenate(colormappings)
    print(colormappings.shape)

    plt.scatter(reduced_coordinates[:,0],reduced_coordinates[:,1],c=colormappings,s=5,cmap=cmap)
    # ticks for scaling
    x_min, x_max = reduced_coordinates[:, 0].min(), reduced_coordinates[:, 0].max()
    y_min, y_max = reduced_coordinates[:, 1].min(), reduced_coordinates[:, 1].max()
    plt.xticks(np.arange(np.floor(x_min), np.ceil(x_max) + 1, 1))
    plt.yticks(np.arange(np.floor(y_min), np.ceil(y_max) + 1, 1))

    plt.grid(visible=False)
    plt.savefig(f"{outfilepath}_crawlhighlights.png")
    plt.close()

#Contour plots 
def contour_embedding_space(outfile_path, embeddingspace_coordinates, levels=10, thresh=0, bw_adjust=.5,
                             title=None, xlabel=None, ylabel=None):
    '''Plots a contour map of embedding space coordinates.

    Parameters
    ----------
    outfile_path : str or None
        Path to save the output plot. If None, defaults to the current working directory.

    embeddingspace_coordinates : array-like, shape = (n_samples, 2)
        The coordinates of your samples in the embedding space created by either UMAP or PCA.
        This function assumes a two-dimensional representation for visualization purposes.
        A Gaussian KDE (via Seaborn) is used to estimate the density.

    levels : int, default = 10
        Number of contour levels to draw.

    thresh : float, default = 0
        Only plot density regions where the estimated value is greater than this threshold.

    bw_adjust : float, default = 0.5
        Bandwidth adjustment factor for the KDE. Lower values give finer detail, higher values
        give smoother estimates.

    title : str, default = None
        Optional title for the plot.

    xlabel : str, default = None
        Optional label for the x-axis.

    ylabel : str, default = None
        Optional label for the y-axis.

    Returns
    -------
    None
        Saves the contour plot to the specified path.

    Notes
    -----
    This function wraps `sns.kdeplot` for quick integration into analysis workflows.
    For more customized control over contour appearance, call `sns.kdeplot` directly
    on the reduced coordinates.

    Examples
    --------
    contour_embedding_space("embedding_contour.png", X_pca, title="Embedding Space",
                            xlabel="PC1", ylabel="PC2")
    '''

    outfile_path = outfile_path if outfile_path is not None else os.getcwd()

    sns.kdeplot(
        x=embeddingspace_coordinates[:, 0],
        y=embeddingspace_coordinates[:, 1],
        fill=True,
        cmap="cividis",
        levels=levels,
        thresh=thresh,
        bw_adjust=bw_adjust,
        cbar=True
    )

    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(False)

    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    plt.grid(visible=False)
    plt.savefig(outfile_path, dpi=800)
    plt.close()

    return


if __name__ == "__main__":
    frame_list=((([80] * 20) + ([160] * 10)) * 2)
    print('running just the visualization module')
    fake_labels=[1]*3200+[2]*3200
    print(fake_labels)
    replicatemap_from_labels(fake_labels,frame_list)