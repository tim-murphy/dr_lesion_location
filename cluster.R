norm <- function(x){(x-min(x))/(max(x)-min(x))}

scatter <- function(data, title, colour="black")
{
    plot(data, col=colour, main=title, xlim=c(0,1100), ylim=c(0,1100),
        xlab="", xaxt="n", ylab="", yaxt="n", pch=".")
}

args = commandArgs(trailingOnly=TRUE)
if (length(args) < 1)
{
    stop("Usage: cluster.R <scatter_csv> [<chart_title>]")
}

chart_title = "Clustered (k=2)"
if (length(args) > 1)
{
    chart_title = args[2]
}

csv_file = args[1]
paste("Using CSV file: ", csv_file)

# load the data from file
raw_data = read.csv(csv_file)

png("Clustering.png")
#pdf("Clustering.pdf")
scatter(raw_data, chart_title)

set.seed(1)
c = stats::kmeans(raw_data, centers=2, nstart=5, iter.max=250, algorithm="Lloyd") #"MacQueen")
scatter(raw_data, chart_title, c$cluster)

dev.off()
warnings()

print("Finished")
