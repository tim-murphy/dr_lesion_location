$lesions = @('EX', 'MA', 'SE', 'HE', 'ALL')

foreach ($l in $lesions)
{
    Write-Output $l
    for ($x = 2; $x -le 10; $x+=1)
    {
        python heatmap_to_scatter.py "lesion_count_both_${l}.csv" "scatter_${l}_threshold.csv" $x
        Rscript cluster.R "scatter_${l}_threshold.csv" "Clustered (threshold = ${x})"
        move Clustering.png "clust_${l}_${x}.png" -force
    }
    python create_gif.py (Get-Item clust_${l}_*.png)
    move animation.gif animation_${l}.gif -force
}
