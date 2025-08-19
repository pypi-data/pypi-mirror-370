CREATE TABLE IF NOT EXISTS conversions (
                series_uid TEXT, study_uid TEXT, nifti TEXT, modality TEXT, mrn TEXT, accession TEXT, series_name TEXT, series_number INTEGER, scan_date TEXT, original_series_name TEXT, study_description TEXT, ct_direction TEXT, image_type TEXT, sex TEXT, age INTEGER, birth_date TEXT, height_m REAL, weight_kg REAL, pregnancy_status INTEGER, pixel_length_mm REAL, pixel_width_mm REAL, slice_thickness_mm REAL, manufacturer TEXT, model TEXT, kvp REAL, sequence_name TEXT, protocol_name TEXT, contrast_bolus_agent TEXT, contrast_bolus_route TEXT, contrast_bolus_volume REAL, dicom_folder TEXT, conversion_date TEXT, PRIMARY KEY (series_uid)
            );
CREATE TABLE IF NOT EXISTS segmentations (
                nifti TEXT, series_uid TEXT, task INTEGER, seg_file TEXT, seg_date TEXT, status TEXT, failed_error TEXT, PRIMARY KEY (nifti, task, seg_date)
            );
CREATE TABLE IF NOT EXISTS metadata (
                nifti TEXT, series_uid TEXT, study_uid TEXT, output_stats_file TEXT, modality TEXT, mrn TEXT, accession TEXT, series_name TEXT, series_number INTEGER, scan_date TEXT, original_series_name TEXT, study_description TEXT, ct_direction TEXT, abdominal_scan INTEGER, chest_scan INTEGER, correct_vertebrae_order INTEGER, lowest_vertebra TEXT, highest_vertebra TEXT, image_type TEXT, sex TEXT, age INTEGER, birth_date TEXT, height_m REAL, weight_kg REAL, pregnancy_status INTEGER, pixel_length_mm REAL, pixel_width_mm REAL, slice_thickness_mm REAL, manufacturer TEXT, model TEXT, kvp REAL, sequence_name TEXT, protocol_name TEXT, contrast_bolus_agent TEXT, contrast_bolus_route TEXT, contrast_bolus_volume REAL, dicom_folder TEXT, conversion_date TEXT, PRIMARY KEY (nifti)
            );
CREATE TABLE IF NOT EXISTS vol_int (
                nifti TEXT, series_uid TEXT, structure TEXT, volume_cm3 REAL, hu_mean REAL, hu_std_dev REAL, PRIMARY KEY (nifti, structure)
            );
CREATE TABLE IF NOT EXISTS contrast (
                nifti TEXT, series_uid TEXT, phase TEXT, probability REAL, pi_time REAL, pi_time_std REAL, PRIMARY KEY (nifti)
            );
CREATE TABLE IF NOT EXISTS vertebrae (
                nifti TEXT, series_uid TEXT, vertebra TEXT, midline INTEGER, PRIMARY KEY (nifti, vertebra)
            );
CREATE TABLE IF NOT EXISTS aorta_metrics (
                nifti TEXT, series_uid TEXT, region TEXT, entire_region INTEGER, length_mm REAL, tortuosity_index REAL, icm REAL, n_inflections INTEGER, peria_volume_cm3 REAL, peria_ring_volume_cm3 REAL, peria_fat_volume_cm3 REAL, peria_hu_mean REAL, peria_hu_std REAL, calc_volume_mm3 REAL, calc_agatston REAL, calc_count INTEGER, is_120_kvp INTEGER, mean_diameter_mm REAL, mean_roundness REAL, mean_flatness REAL, PRIMARY KEY (nifti, region)
            );
CREATE TABLE IF NOT EXISTS aorta_diameters (
                nifti TEXT, series_uid TEXT, region TEXT, measure TEXT, mean_diameter_mm REAL, major_diameter_mm REAL, minor_diameter_mm REAL, area_mm2 REAL, roundness REAL, flatness REAL, rel_distance REAL, entire_region INTEGER, PRIMARY KEY (nifti, region, measure)
            );
CREATE TABLE IF NOT EXISTS tissues_volumetric (
                nifti TEXT, series_uid TEXT, region TEXT, structure TEXT, volume_cm3 REAL, hu_mean REAL, hu_std_dev REAL, PRIMARY KEY (nifti, region, structure)
            );
CREATE TABLE IF NOT EXISTS tissues_vertebral (
                nifti TEXT, series_uid TEXT, vertebra TEXT, structure TEXT, measurement TEXT, value REAL, PRIMARY KEY (nifti, vertebra, structure, measurement)
            );
CREATE TABLE IF NOT EXISTS iliac (
                nifti TEXT, series_uid TEXT, side TEXT, length_mm REAL, location TEXT,  metric TEXT, value REAL, PRIMARY KEY (nifti, side, location, metric)
)
