import argparse
import json
import os
import re
from glob import glob

# Convert CoNLL-2014 SGML to BEA-2019 JSON data.
# Note: If the SGML is malformed, one fix is to replace: <P>\n<P> with </P>\n<P>
def main(args):
	# Get all the xml files in the input dir
	sgml_files = sorted(glob(args.sgml_dir+"/*.sgml"))
	# Print error and quit if no files found.
	if not sgml_files:
		print("ERROR: No sgml files found in \'"+args.sgml_dir+"\'!")
		exit()

	# Store essays as lists of paragraphs
	essays = []
	coder_edits = {}
	# Loop through all the SGML files for each annotator.
	for coder, sgml_file in enumerate(sgml_files):
		# Open the file
		with open(sgml_file) as sgml:
			# Read the file
			data = sgml.read()
			# Get all the documents
			docs = re.findall("<DOC.*?</DOC>", data, re.DOTALL)
			# Loop through the documents
			for doc_id, doc in enumerate(docs):
				# If this is the first annotator, get the essay text
				if coder == 0:
					# Get the title and paragraphs
					title = re.findall("<TITLE>\n(.*?)</TITLE>", doc, re.DOTALL)
					paras = re.findall("<P>\n(.*?)</P>", doc, re.DOTALL)
					# Title is treated as a paragraph.
					paras = title + paras if title else paras
					# Save the essay paragraphs
					essays.append(paras)
				# Extract the edits
				edits = re.findall("<MISTAKE (.*?)</MISTAKE>", doc, re.DOTALL)
				proc_edits = []
				cur_para = 0 
				prev_edit_end = 0
				# Loop through the edits
				for edit in edits:
					edit = edit.strip()
					# Get the error type and correction
					cat = re.findall("<TYPE>(.*?)</TYPE>", edit, re.DOTALL)[0]
					cor = re.findall("<CORRECTION>(.*?)</CORRECTION>", edit, re.DOTALL)[0]
					# Replace newlines inside corrections with whitespace
					cor = cor.replace("\n", " ").strip()
					# Get the edit offsets
					offsets = edit.split('"')
					para_id = int(offsets[1])
					start = int(offsets[3])
					end = int(offsets[7])
					# FILTERS
					# Ignore edits that cross paragraph boundaries
					if offsets[1] != offsets[5]: continue
					# Ignore edits longer than 40 chars in orig or cor; ~3.5% of all edits
					if end-start > 40 or len(cor) > 40: continue
					# Ignore Citation edits and edits containing ellipses (lazy annotators!)
					if cat == "Cit": continue
					if "..." in cor: continue
					# Set the correction string of Unclear Meaning (Um) edits to None for detection.
					if cat == "Um": cor = None
					# Set prev_edit_end to 0 for each new para.
					prev_edit_end = prev_edit_end if para_id == cur_para else 0	
					# Ignore edits that overlap with previous edits in the same para.
					if start < prev_edit_end: continue
					# Update cur_para and prev_edit_end
					cur_para = para_id
					prev_edit_end = end
					# Update edit character spans in relation to the whole text
					para_offset = len("".join(essays[doc_id][0:para_id]))
					start += para_offset
					end += para_offset
					proc_edits.append([start, end, cor, cat])
				# Save the edits for this doc for each coder
				if coder not in coder_edits: coder_edits[coder] = []
				coder_edits[coder].append(proc_edits)

	# Open output file
	with open(args.out, "w", encoding='utf-8') as out:
		# Write the info to json output
		for essay_id, essay in enumerate(essays):
			output = {}
			# Combine the paragraphs
			essay = "".join(essay)
			output["text"] = essay
			# Get the edits for each coder for each essay
			essay_edits = []
			for coder, edits in coder_edits.items():
				essay_edits.append([coder, edits[essay_id]])
			output["edits"] = essay_edits
			json.dump(output, out, ensure_ascii=False)
			out.write("\n")

if __name__ == "__main__":
	# Define and parse program input
	parser = argparse.ArgumentParser(description="Convert CoNLL/NUCLE SGML data to JSON.")
	parser.add_argument("sgml_dir", help="The path to a directory containing SGML files.")
	parser.add_argument("-out", help="Output JSON filename.", required=True)
	args = parser.parse_args()
	# Check if input is a valid dir.
	if not os.path.isdir(args.sgml_dir):
		print("ERROR: \'"+args.sgml_dir+"\' is not a directory!")
		exit()
	# Run the main program.
	main(args)