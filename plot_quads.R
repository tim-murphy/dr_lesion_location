# Split the raw pixel count data at the mac into quads and plot the data.

library(FSA)
library(rcompanion)

# globals
P <- 0.05
QUAD_SIZE_X <- 200
QUAD_SIZE_Y <- QUAD_SIZE_X

# approximating enumerations
SIDE <- function()
{
    list(RIGHT = "right", LEFT = "left", BOTH = "both")
}

LESION <- function()
{
    list(EXUDATES = "EX",
         HAEMORRHAGES = "HE",
         MICROANEURYSMS = "MA",
         COTTONWOOLSPOTS = "SE",
         ALL = "ALL")
}

print_matrix_size <- function(m)
{
    cat("Matrix: rows =", nrow(m), " cols =", ncol(m), "\r\n")
}

sample_stats <- function(s)
{
    print(summary(s))
    cat("sd=", sd(s), "\r\n")
}

tee_to_file <- function(string, file)
{
    print(string)
    capture.output(string, file=file, append=TRUE)
}

process_lesion <- function(lesion, side = SIDE()$BOTH)
{
    print(paste("Processing lesion type:", lesion, "on", side, "eye(s)"))

    csv_file <- paste("lesion_count_", side, "_", lesion ,".csv", sep="")
    out_file <- paste("analysis_", side, "_", lesion, ".txt", sep="")
    cat("", file=out_file, append=FALSE) # create/clear the output file

    pdf(paste("plots_", side, "_", lesion, ".pdf", sep=""))

    print("Loading data from CSV")
    # load all of the raw data into a matrix
    raw_data <- NULL
    for (line in read.csv(csv_file, header=FALSE, sep=",", dec=".", strip.white=TRUE))
    {
        raw_data <- rbind(raw_data, matrix(line, nrow=1))
    }

    print("Splitting into quadrants")
    # the macular is used as the origin
    mac_coords_right <- c(450, 525)
    mac_coords_left <- c(650, 525)
    mac_coords <- mac_coords_right
    if (side == SIDE()$LEFT)
    {
        mac_coords <- mac_coords_left
    }

    quads_min_x = mac_coords[1] - QUAD_SIZE_X
    quads_max_x = mac_coords[1] + QUAD_SIZE_X
    quads_min_y = mac_coords[2] - QUAD_SIZE_Y
    quads_max_y = mac_coords[2] + QUAD_SIZE_Y

    # temporal quads are on the left side for right eye and combined, and right
    # side for left eye
    quad_st = quad_sn = quad_it = quad_in = NULL

    if (side == SIDE()$LEFT)
    {
        quad_sn = raw_data[quads_min_x:mac_coords[1], quads_min_y:mac_coords[2]]
        quad_st = raw_data[(mac_coords[1]+1):quads_max_x, quads_min_y:mac_coords[2]]
        quad_in = raw_data[quads_min_x:mac_coords[1], (mac_coords[2]+1):quads_max_y]
        quad_it = raw_data[(mac_coords[1]+1):quads_max_x, (mac_coords[2]+1):quads_max_y]
    }
    else
    {
        quad_st = raw_data[quads_min_x:mac_coords[1], quads_min_y:mac_coords[2]]
        quad_sn = raw_data[(mac_coords[1]+1):quads_max_x, quads_min_y:mac_coords[2]]
        quad_it = raw_data[quads_min_x:mac_coords[1], (mac_coords[2]+1):quads_max_y]
        quad_in = raw_data[(mac_coords[1]+1):quads_max_x, (mac_coords[2]+1):quads_max_y]
    }

    print("Performing Kruskal-Wallis test")
    # Kruskal-Wallis test
    # first, put all data into a giant data frame
    col_names = c("Quad", "Count")
    quad_factors = factor(c("ST", "SN", "IT", "IN"))

    st_frame = data.frame("ST", c(quad_st), stringsAsFactors=TRUE)
    names(st_frame) = col_names
    sn_frame = data.frame("SN", c(quad_sn), stringsAsFactors=TRUE)
    names(sn_frame) = col_names
    it_frame = data.frame("IT", c(quad_it), stringsAsFactors=TRUE)
    names(it_frame) = col_names
    in_frame = data.frame("IN", c(quad_in), stringsAsFactors=TRUE)
    names(in_frame) = col_names
    all_quads_frame = rbind(st_frame, sn_frame, it_frame, in_frame)
    tee_to_file(kruskal.test(Count ~ Quad, data=all_quads_frame), out_file)

    print("Performing Dunn test")
    # follow up with a Dunn test to see which quads are different
    # method="bh" means we adjust p-values for multiple comparisons
    dt = dunnTest(Count ~ Quad, data=all_quads_frame, method="bh")
    tee_to_file(dt, out_file)

    # use a nicer table to show differences. Same letters means no difference.
    tee_to_file(cldList(comparison=dt$res$Comparison, p.value=dt$res$P.adj, threshold=P), out_file)

    print("Performing ANOVA")
    # ANOVA (even though the data is not normally distributed)
    anova = aov(Count ~ Quad, data=all_quads_frame)
    tee_to_file(summary(anova), out_file)

    print("Performing TukeyHSD")
    # pairwise comparisons from ANOVA
    tee_to_file(TukeyHSD(anova), out_file)

    print("Generating normalcy plots")
    # and some plots
    plot(anova, 1)
    plot(anova, 2)

    # histograms by group
    print("Generating histograms")
    hist(Count ~ Quad, data=all_quads_frame)

    # boxplot each quadrant
    print("Generating boxplots")
    boxplot_labels = c("Supratemporal", "Supranasal",
                       "Infratemporal", "Infranasal")
    boxplot(Count ~ Quad, data=all_quads_frame,
            names=boxplot_labels,
            xlab="Quadrant",
            ylab="Lesion Count Per Pixel")

    # bar graph of total pixel counts
    # do it as a percentage as this is easier to understand
    print("Generating bar graphs - total count")
    quad_sums = c(sum(quad_st), sum(quad_sn),
                  sum(quad_it), sum(quad_in)) 
    quad_sums = quad_sums / sum(quad_sums) * 100
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

    print("Dataset finished")
    print("=-=-=-=-=-=-=-=-")
    print("")
}

for (l in LESION())
{
    for (s in SIDE())
    {
        process_lesion(l, s)
    }
}

"done"
