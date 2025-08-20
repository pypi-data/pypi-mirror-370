from fileflix import read_file, write_file

# Read any file
df = read_file("data.csv")

# Write to another format
write_file(df,"output.xlsx")