# MirCAT-v2
Mirshahi-Lab CT Analysis Toolkit (MirCAT). Convert dicoms, segment niftis, extract data.  
V1 has been archived. This version is almost a full rewrite of the segmentation section, specifically to incorporate nnUNet models directly into the pipeline.


# NOTES
When using docker -> make sure to add the --ipc=host flag or segmentation will not work