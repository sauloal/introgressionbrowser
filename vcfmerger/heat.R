#install.packages("heatmap.plus")
#library("heatmap.plus")
#require("heatmap.plus")


#source("http://www.bioconductor.org/biocLite.R")
#biocLite("ALL")
library("ALL")
data("ALL")


# IF R > 3.0
#source("http://www.bioconductor.org/biocLite.R")
#install.packages("gplots")
#biocLite("gplots")

# ELSE
#wget http://cran.r-project.org/src/contrib/Archive/gplots/gplots_2.11.0.tar.gz
#wget http://cran.r-project.org/src/contrib/Archive/gtools/gtools_2.7.0.tar.gz
#wget http://cran.r-project.org/src/contrib/Archive/gdata/gdata_2.12.0.tar.gz
#wget http://cran.r-project.org/src/contrib/Archive/caTools/caTools_1.13.tar.gz

#install.packages("gtools_2.7.0.tar.gz", repos=NULL, type="source")
#install.packages("gdata_2.12.0.tar.gz", repos=NULL, type="source")
#install.packages("caTools_1.13.tar.gz", repos=NULL, type="source")
#install.packages("gplots_2.11.0.tar.gz", repos=NULL, type="source")

library("gplots")


in_csv    <- "/tmp/heat.csv"
main_name <- "Gene by gene phylogeny :: Chromosome <CHROMOSOME> :: Reference <REF>"
x_name    <- "Gene name"
y_name    <- "Species"

img_height  = 2048
img_width   = img_height * 3
img_dpi     = 500
img_cex_row = 0.25
img_cex_col = 0.15
pdf_height  = 22
pdf_width   = pdf_height * 3
pdf_cex_row = 1
pdf_cex_col = .8

#nba <- read.csv("/tmp/heat.csv", sep=",")
#nba <- read.csv(file="/dev/stdin", sep=",", header=TRUE)
nba <- read.csv(file=in_csv, sep=",", header=TRUE)
#nba

row.names( nba ) <- nba$name
nba <- nba[,2:length(nba)]

#nba

nba_matrix     <- data.matrix( nba )


#http://www2.warwick.ac.uk/fac/sci/moac/people/students/peter_cock/r/heatmap/
#nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=cm.colors(256), scale="column", margins=c(5,10)) # blue
#nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10)) # red
#nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
#nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
#nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
#nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), cexRow=0.5, main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
#nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), cexRow=0.5, cexCol=0.1, main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
#density.info="none",
#topo.colors(50) # blue-gree-yellow



png("heat.png", width=img_width, height=img_height, bg="transparent", units="px", res=img_dpi, type="cairo-png", antialias="none")
nba_heatmap <- heatmap.2(nba_matrix, col=topo.colors(50), symkey=FALSE, trace="none", scale="column", margins=c(5,10), key=TRUE, cexRow=img_cex_row, cexCol=img_cex_col, main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram

pdf("heat.pdf", width=pdf_width, height=pdf_height, title=main_name, compress=TRUE)
nba_heatmap <- heatmap.2(nba_matrix, col=topo.colors(50), symkey=FALSE, trace="none", scale="column", margins=c(5,10), key=TRUE, cexRow=pdf_cex_row, cexCol=pdf_cex_col, main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
