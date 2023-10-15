# Bike Computer Forensics: an efficient and robust method for FIT file recovery
This research aims to recover as many data messages as possible in the corrupted FIT file by using 3 phases of recovery method.

Presented at `DFRWS APAC 2023`.
https://doi.org/10.1016/j.fsidi.2023.301606

## Summary of our proprosed recovery method

### Phase-1: Search definition messages
Find the start offset of each definition message(Global Message Number: RECORD -> Ride Data) in the file.

### Phase-2: Generate regex to search data messages
Make a definition message(RECORD) lookup table while parsing the data.
When it hits the error due to the corruption, it will make a list of regex based on the lookup table.

### Phase-3: Minimize false-negatives and positives
Use sliding window pattern match to minimize false-positives & negatives.

