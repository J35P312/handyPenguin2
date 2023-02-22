import xlrd
import json
import os
import copy



main_template={
  "name": "Name",
  "customer": "cust032",
  "comment": "Automatically generated by the Handy Penguin V1.1.1",
  "samples": []
}

sample_template={
      "name": "SampleName",
      "application": "RMLP05R800",
      "data_analysis": "fluffy",
      "data_delivery": "statina",
      "comment": "",
      "control": "",
      "volume": "100",
      "concentration": "10",
      "concentration_sample":"SampleConcentration",
      "pool": "Pool",
      "rml_plate_name": "",
      "well_position_rml": "",
      "index": "KAPA UDI NIPT",
      "index_number": "IndexNumber",
      "index_sequence": "IndexSequence",
      "priority": "priority"
}

def read_index_file(index_per_well,index_id_per_well,index_file_path,index_id,wd):
	try:
		for line in open(index_file_path):
			content=line.strip().split()
			index_per_well[content[0]]="{} ({}-{})".format(content[1],content[2],content[3])
			index_id_per_well[content[0]]=index_id
	except:
		f=open("{}/error.txt".format(wd),"w")
		f.write("Kunde ej läsa index filen:{}".format(index_file_path))
		quit()

	return(index_per_well,index_id_per_well)


wd=os.path.dirname(os.path.realpath(__file__))

files = os.listdir(wd)

for f in files:
	if not f.endswith(".xls"):
		continue

	name=f.split("_")[-1].split(".")[0]
	try:
		os.mkdir(name)
	except:
		pass
	
	sample_data=[]

	wb = xlrd.open_workbook(f.strip())
	sheet = wb.sheet_by_index(0)

	index_per_well={}
	index_id_per_well={}

	missing_index=False
	for i in range(1,sheet.nrows):
		sample_data.append(copy.deepcopy(sample_template))
		sample_data[-1]["name"]=sheet.cell_value(i, 2)
		sample_data[-1]["comment"]=sheet.cell_value(i, 1)
		well=sheet.cell_value(i, 1)

		if "Set1" in sheet.cell_value(i, 4):
			if not index_per_well:
				index_per_well,index_id_per_well=read_index_file(index_per_well,index_id_per_well,"kapa_index_1.swap.tab","index1",wd)
			sample_data[-1]["index_number"]=str(index_per_well[ well ].split(" ")[0].replace("UDI",""))
			sample_data[-1]["index_sequence"]=index_per_well[ well ]
			#sample_data[-1]["index"]=index_id_per_well[ well ]

		elif "Set2" in sheet.cell_value(i, 4):
			if not index_per_well:
				index_per_well,index_id_per_well=read_index_file(index_per_well,index_id_per_well,"kapa_index_2.swap.tab","index2",wd)

			sample_data[-1]["index_number"]=str(index_per_well[ well ].split(" ")[0].replace("UDI",""))
			sample_data[-1]["index_sequence"]=index_per_well[ well ]
			#sample_data[-1]["index"]=index_id_per_well[ well ]
		else:
			missing_index=True

		sample_data[-1]["pool"]=name+"_NIPT"
		sample_data[-1]["concentration_sample"]=str(sheet.cell_value(i, 3))


	main_template["name"]=str(name)+"_NIPT"
	main_template["samples"]=sample_data
	if missing_index:
		outfile="{}/FEL.txt".format(name,name)
		o=open(outfile,"w")
		o.write("Index saknas! Ange set1 eller set2 i \"Index Plate\" kolumnen.")
		o.close()
		continue

	outfile="{}/{}_nipt_rml.json".format(name,name)
	o=open(outfile,"w")
	o.write(json.dumps(main_template,indent=4)) 
	o.close()
	try:
		os.rename(f, "{}/{}".format(name,f))
	except:
		pass
