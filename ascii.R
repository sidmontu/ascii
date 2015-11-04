library(jpeg)
#library(MASS) #for pseudo-inverse implementation only

#read in arguments
args <- commandArgs(trailingOnly = TRUE)
imgPath <- args[1]
#create output image path
outImgPath <- paste("results/",gsub("^(.*[/])","",imgPath),sep="")

#global constants
num_glyphs <- 95
glyph_size <- 19*38
beta <- 2 #SED = 2, KLD = 1
epsilon <- 0 #threshold, for maxcol(H)
num_iterations <- as.numeric(args[2]) #number of H update iterations

#read in image & convert to grayscale, if needed
img <- readJPEG(imgPath)
if (length(dim(img)) == 3){
  #convert image to grayscale using luminosity method -- 0.21 R + 0.72 G + 0.07 B
  bw_img <- matrix(, nrow = nrow(img), ncol = ncol(img))
  for (i in 1:nrow(img)){
    for (j in 1:ncol(img)){
      bw_img[i,j] <- 0.21*img[i,j,1] + 0.72*img[i,j,2] + 0.07*img[i,j,3]
    }
  }  
} else {
  bw_img <- img
}

#partition the input image
#define P and Q, and the glyph dimensions
P <- nrow(bw_img)
Q <- ncol(bw_img)
g_row <- 38 #height of glyph = nrow(glyph_matrix) = N
g_col <- 19 #width of glyph = ncol(glyph_matrix) = M

#start by one-padding the rows
one_col <- rep(1,times=Q)
if (P%%g_row != 0){
  rem <- g_row - P%%g_row
  for (i in (P+1):(P+rem)){
    bw_img <- rbind(bw_img,one_col)
  }
} else {
  rem <- 0
}

#update new row dimension, P
P <- P + rem

#generate new column vector based on new P
one_row <- rep(1,times=P)

#zero-pad the columns
if (Q%%g_col != 0){
  rem <- g_col - Q%%g_col
  for (i in (Q+1):(Q+rem)){
    bw_img <- cbind(bw_img,one_row)
  }
} else {
  rem <- 0
}

#update to the new Q
Q <- Q + rem

# now take g_row and g_col blocks one at a time
# convert them into vectors, and create V,
# where each column in V is the block vector
num_blocks_per_row <- P / g_row
num_blocks_per_col <- Q / g_col

V <- matrix(, nrow = g_row*g_col, ncol = num_blocks_per_row*num_blocks_per_col)
for (i in 1:num_blocks_per_row){
  for (j in 1:num_blocks_per_col){
    v <- vector()
    #construct column-vector of image-block
    for (x in 1:g_col){
      for (y in 1:g_row){
        v <- c(v,bw_img[(i-1)*g_row+y,(j-1)*g_col+x])
      }
    }   
    V[,(i-1)*num_blocks_per_col+j] <- v#/sqrt(sum(v^2))
  }
}

#read in glyphs to construct the matrix W
W <- matrix(, ncol = num_glyphs, nrow = glyph_size)

glyphDir <- "./Courier-Glyphs/"
for (i in 32:126){ #32:126 --> numbering of glyph file name
  filename <- paste(glyphDir,i,".jpg",sep="")
  glyph <- readJPEG(filename)
  glyph <- as.vector(glyph) #column-wise unroll (!)
  l2norm <- sqrt(sum(glyph^2))
  glyph <- glyph/l2norm
  W[,i-31] <- glyph
}


########################## FITTING ###########################
#construct random matrix H, initialize with random positive values
H <- matrix(runif(num_glyphs * num_blocks_per_row*num_blocks_per_col)+1, nrow = num_glyphs, ncol = num_blocks_per_row*num_blocks_per_col)

############################################################
# This is the method optimized for speed,
# uses linear algebra routines
############################################################
for (t in 1:num_iterations){
  print(paste("Running iteration number ",t,sep=""))  
  WH <- W %*% H    
  WH_num <- V/(WH^(2-beta))
  WH_den <- WH^(beta-1)
  H_next <- H * (t(W) %*% WH_num)/(t(W) %*% WH_den)
  H <- H_next
  # check and remove NaNs
  H_vec <- as.vector(H)
  H_vec[!is.finite(H_vec)] <- 0
  H <- matrix(H_vec,nrow = num_glyphs, ncol = num_blocks_per_row*num_blocks_per_col)
}

#################################################################
# This is the slow method for fitting -- nested for-loops with 
# lots of irregular memory access patterns,
# resulting in very slow performance.
#################################################################
# for (t in 1:num_iterations){
#   print(paste("Running iteration number ",t,sep=""))
#   WH <- W %*% H
#   WH_num <- WH^(2-beta)
#   WH_den <- WH^(beta-1)
#   for (j in 1:nrow(H)){
#     for (k in 1:ncol(H)){      
#       numerator <- 0
#       denominator <- 0
#       #print(paste("t = ",t,", j = ",j,", k = ",k,sep=""))
#       for (i in 1:nrow(V)){
#         numerator <- numerator + W[i,j]*(V[i,k]/WH_num[i,k])
#         denominator <- denominator + W[i,j]*WH_den[i,k]
#       }
#       H[j,k] <- H[j,k] * numerator/denominator
#     }
#   }
# }

##########################################################
# This is the pseudo-inverse method.. very slow and gets
# increasingly slower as size of image increases
##########################################################
#H <- ginv(t(W)%*%W)
#A <- t(W)%*%V
#H <- H%*%A
#H <- H/sum(H)

#maxcol(H,e) to find which glyph to fit
max_col_indices <- max.col(t(H))
max_col_vals <- vector()
for (i in 1:length(max_col_indices)){
  max_col_vals <- c(max_col_vals,H[max_col_indices[i]],i)
}
identity_H <- matrix(0,nrow = num_glyphs, ncol = num_blocks_per_row*num_blocks_per_col)
for (i in 1:length(max_col_indices)){
  if (max_col_vals[i] > epsilon){
    identity_H[max_col_indices[i],i] <- 1
  } else {
    identity_H[1,i] <- 1
  }
}

#reconstruction
ascii_img <- matrix(,nrow = P, ncol = Q)
for (i in 1:num_blocks_per_row){
  for (j in 1:num_blocks_per_col){
    index <- (i-1)*num_blocks_per_col + j
    chosenGlyph <- paste(glyphDir,(max_col_indices[index]+31),".jpg",sep="")
    glyph <- readJPEG(chosenGlyph)
    row <- 1 + (i-1)*g_row
    col <- 1 + (j-1)*g_col
    ascii_img[row:(row+g_row-1),col:(col+g_col-1)] <- glyph
  }
}

#output the image
writeJPEG(ascii_img,target=outImgPath,quality=1)
