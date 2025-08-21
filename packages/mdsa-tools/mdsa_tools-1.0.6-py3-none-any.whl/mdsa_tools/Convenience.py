
#--------------------------------------------------------------------------------------------------
#Use lists 1 and 2-   
#   Numbering for the restrained and unrestrained residues in our system 
#   Note: they are 1 indexed while mdtraj is generally 0 indexed, also we keep theese together
#         because it made the indexing easier.
#--------------------------------------------------------------------------------------------------

restrained_residues = [
    1, 2, 3, 4, 5, 6, 7,
    8, 9, 10, 11, 12, 17, 18, 19, 20, 21, 22, 32, 33,
    34, 35, 36,
    37, 38, 39, 40, 41, 42, 43, 44, 45, 52, 53,
    54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 74, 77, 78,
    79, 80, 81, 82,
    83, 84, 85, 86, 87, 105, 106, 107, 108, 109, 110, 111,
    112, 113, 114, 115,
    116, 117, 118,
    119, 120, 121, 142, 143, 144, 145, 146, 147, 148, 149,
    150, 151, 152, 153, 154,
    155, 156, 157, 158, 159, 160, 161, 162, 163, 176, 177, 178, 179, 180, 181,
    182, 183, 196, 199, 200, 201, 202,
    203, 204, 205, 206,
    207, 208,
    209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 224, 225, 226, 227,
    228, 229, 247, 248, 249, 250, 251, 252, 253,
    254, 255, 270, 271,
    272, 273, 274, 275, 276, 277,
    278, 279, 280, 281, 282, 283, 284,
    285, 286, 287, 290, 291, 292, 293, 294, 295, 296,
    297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312,
    313, 314, 315, 316,
    317, 318, 319, 331,
    332, 333, 334, 335, 336,
    337, 338, 339, 340, 341,
    342, 343, 344, 345, 363, 364, 365,
    366, 367, 368, 369, 390, 391, 392, 393,
    394, 395, 396, 397,
    398, 399, 400, 416, 417, 418,
    419, 431,
    432, 433, 434, 435,
    436, 437, 438, 439, 440, 441, 442,
    443, 453, 454, 455, 456, 457, 458,
    459, 460, 469, 470, 471,
    472, 473, 474, 475,
    476, 477, 478, 479, 490, 491,
    492, 493, 494
]

unrestrained_residues = [
    res for res in range(1, 495) if res not in restrained_residues
]

#--------------------------------------------------------------------------------------------------
#Indexes for the decoding center of the ribosome 
#   Note: they are 1 indexed while mdtraj is generally 0 indexed
#--------------------------------------------------------------------------------------------------

Asite_list=[94,127,240,408,409,410,423,424,425,426,427,428]

#--------------------------------------------------------------------------------------------------
#Test list 1- 
#   General tests of the efficacy of our tools, here we create specifically numbering to make sure
#   our formatting function for 1 dimensional value vectors is able to accurately display the different
#   replicates in our system
#--------------------------------------------------------------------------------------------------

short_runs_x = [0] * 80
short_replicates_x = short_runs_x * 20  

long_runs_x = [1] * 160
long_replicates_x = long_runs_x * 10

short_runs_y = [2] * 80
short_replicates_y = short_runs_y * 20  

long_runs_y = [3] * 160
long_replicates_y = long_runs_y * 10

test_list=short_replicates_x+long_replicates_x+short_replicates_y+long_replicates_y

#--------------------------------------------------------------------------------------------------
#test list 2- 
#   See test list 1, except this has different numbering for the first and second halves of the Weir 
#   lab in particular's variable data
#--------------------------------------------------------------------------------------------------


short_runs_x_2 = [1] * 80
short_replicates_x_2 = short_runs_x_2 * 20  
long_runs_x_2 = ([2] * 80)+([3]*80)
long_replicates_x_2 = long_runs_x_2 * 10


short_runs_y_2 = [4] * 80
short_replicates_y_2 = short_runs_y_2  * 20  
long_runs_x_2 = ([5] * 80)+([6]*80)
long_replicates_y_2 = long_runs_x_2 * 10



test_list_2=short_replicates_x_2+long_replicates_x_2+short_replicates_y_2+long_replicates_y_2



#--------------------------------------------------------------------------------------------------
#test list 3- 
#   A fake PCA output meant for running a test of PCA plotting on our data
#--------------------------------------------------------------------------------------------------


# ------------------------------
# Updated test_list_3
# ------------------------------

short_runs_x_3 = [1] * 80
short_replicates_x_3 = short_runs_x_3 * 20  

long_replicates_x_3 = []
for i in range(10):
    long_replicates_x_3.extend([10 + i] * 80)  # labels 10–19 for first long set
for i in range(10):
    long_replicates_x_3.extend([20 + i] * 80)  # labels 20–29 for second long
short_runs_y_3 = [4] * 80
short_replicates_y_3 = short_runs_y_3 * 20  

# Long
long_replicates_y_3 = []
for i in range(10):
    long_replicates_y_3.extend([30 + i] * 80)  # labels 30–39 for third long set
for i in range(10):
    long_replicates_y_3.extend([40 + i] * 80)  # labels 40–49 for fourth long set

# Final test list
test_list_3 = short_replicates_x_3 + long_replicates_x_3 + short_replicates_y_3 + long_replicates_y_3

