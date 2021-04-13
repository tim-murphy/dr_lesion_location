# Split the raw pixel count data at the mac into quads and plot the data.

library(FSA)
library(rcompanion)

print_matrix_size <- function(m)
{
    cat("Matrix: rows =", nrow(m), " cols =", ncol(m), "\r\n")
}

sample_stats <- function(s)
{
    print(summary(s))
    cat("sd=", sd(s), "\r\n")
}

lesion <- "EX"

file <- paste("lesion_count_both_", lesion ,".csv", sep="")
file

# load all of the raw data into a matrix
raw_data <- NULL
for (line in read.csv(file, header=FALSE, sep=",", dec=".", strip.white=TRUE))
{
    raw_data <- rbind(raw_data, matrix(line, nrow=1))
}

# split the data into quadrants
# the macular is used as the origin
mac_coords_right <- c(450, 525)
mac_coords_left <- c(650, 525)
mac_coords <- mac_coords_right

quad_st = raw_data[0:mac_coords[1], 0:mac_coords[2]]
quad_sn = raw_data[(mac_coords[1]+1):(ncol(raw_data)), 0:mac_coords[2]]
quad_it = raw_data[0:mac_coords[1], (mac_coords[2]+1):(nrow(raw_data))]
quad_in = raw_data[(mac_coords[1]+1):(ncol(raw_data)), (mac_coords[2]+1):(nrow(raw_data))]

# Kruskal-Wallis test
# first, put all data into a giant data frame
col_names = c("Quad", "Count")
st_matrix = data.frame("ST", c(quad_st), stringsAsFactors=TRUE)
names(st_matrix) = col_names
sn_matrix = data.frame("SN", c(quad_sn), stringsAsFactors=TRUE)
names(sn_matrix) = col_names
it_matrix = data.frame("IT", c(quad_it), stringsAsFactors=TRUE)
names(it_matrix) = col_names
in_matrix = data.frame("IN", c(quad_in), stringsAsFactors=TRUE)
names(in_matrix) = col_names
all_quads_matrix = rbind(st_matrix, sn_matrix, it_matrix, in_matrix)
kruskal.test(Count ~ Quad, data=all_quads_matrix)

# follow up with a Dunn test to see which quads are different
p <- 0.05

# method="bh" means we adjust p-values for multiple comparisons
dt = dunnTest(Count ~ Quad, data=all_quads_matrix, method="bh")
print(dt)

# use a nicer table to show differences. Same letters means no difference.
cldList(comparison=dt$res$Comparison, p.value=dt$res$P.adj, threshold=p)

pdf(paste("plots_", lesion, ".pdf", sep=""))

# boxplot each quadrant
print("Generating boxplots")
boxplot_labels = c("Supratemporal", "Supranasal",
                   "Infratemporal", "Infranasal")
boxplot(c(quad_st), c(quad_sn),
        c(quad_it), c(quad_in),
        names=boxplot_labels)

# bar graph of total pixel counts
# do it as a percentage as this is easier to understand
print("Generating bar graphs - total count")
quad_sums = c(sum(quad_st), sum(quad_sn),
              sum(quad_it), sum(quad_in)) 
quad_sums = quad_sums / sum(raw_data) * 100
barplot(quad_sums, names=boxplot_labels,
        xlab="Quadrant", ylab="Lesion Points (%)")

# bar graph of mean lesions mapped to each pixel
print("Generating bar graphs - mean per pixel")
quad_mean = c(mean(quad_st), mean(quad_sn),
              mean(quad_it), mean(quad_in)) 
barplot(quad_mean, names=boxplot_labels,
        xlab="Quadrant", ylab="Mean Lesion Count Per Pixel")

# pie chart :)
print("Generating pie graph")
pie(quad_sums, labels=paste(paste(boxplot_labels, round(quad_sums)), "%", sep=""))

dev.off()

"done"
