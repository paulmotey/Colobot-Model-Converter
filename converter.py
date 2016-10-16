#-*- coding: utf-8 -*-
# Colobot Model Converter
# Version 1.6
# Copyright (c) 2014 Tomasz Kapuściński

import sys
import os.path
from os.path import join, getsize
import os
import geometry
import modelformat
import re
import shutil
from shutil import copyfile
from PIL import Image

image_code=r'map_Kd '
pattern = re.compile(image_code)


# put libraries with model format implementations here
import objformat
import colobotformat
#import colladaformat

# parse arguments
i = 1
n = len(sys.argv)
image_mode = False
dir_mode = False
batch_mode = False
file_list = []

in_dir = None
in_filename = None
in_format = 'default'
in_params = {}

out_dir= None
out_filename = None
out_format = 'default'
out_params = {}

while i < n:
    arg = sys.argv[i]

    if arg == '-i':
        in_filename = sys.argv[i+1]
        i = i + 2
    elif arg == '-if':
        in_format = sys.argv[i+1]
        i = i + 2
    elif arg == '-id':
        in_params['directory'] = sys.argv[i+1]
        i = i + 2
    elif arg == '-ip':
        text = sys.argv[i+1]

        if '=' in text:
            pair = text.split('=')
            in_params[pair[0]] = pair[1]
        else:
            in_params[text] = 'none'

        i = i + 2
    elif arg == '-o':
        out_filename = sys.argv[i+1]
        i = i + 2
    elif arg == '-of':
        out_format = sys.argv[i+1]
        i = i + 2
    elif arg == '-od':
        out_params['directory'] = sys.argv[i+1]
        i = i + 2
    elif arg == '-op':
        text = sys.argv[i+1]

        if '=' in text:
            pair = text.split('=')
            out_params[pair[0]] = pair[1]
        else:
            out_params[text] = 'none'

        i = i + 2
    elif arg == '-batch':
        batch_mode = True
        i = i + 1
    elif arg == '-add':
        file_list.append(sys.argv[i+1])
        i = i + 2
    elif arg == '-addlist':
        listfile = open(sys.argv[i+1], 'r')

        for line in listfile.readlines():
            if len(line) == 0: continue
            if line[-1] == '\n': line = line[:-1]
            file_list.append(line)

        listfile.close();
        i = i + 2
    elif arg == '-f':
        modelformat.print_formats()
        exit()
    elif arg == '-ext':
        modelformat.print_extensions()
        exit()
    elif arg == '-di':
        in_dir=sys.argv[i+1]
        i = i + 2
    elif arg == '-do':
        out_dir=sys.argv[i+1]
        i = i + 2
    elif arg == '-blenderTool':
        dir_mode=True
        i = i + 1
    elif arg == '-image':
        image_mode=True
        i = i + 1
    else:
        print('Unknown switch: {}'.format(arg))
        exit()

# convert all files in a directory
'''
Warning! YMMV
Expects that the directory where it is run contains the source directory for whatever is to be converted
Expects that image files matching those in the mtl file are somewhere on the directory tree " above and sideways "


All commands need this
-do is output directory
-di is input directory


A:
Blend OBJ conversion:: command options are  -blenderTool -of obj
1. convert to obj in blend dir
2. search mtl file for images
3. if image found and it doesn't already exist there, copy it to the obj dir
4. if not found complain that there are missing textures
5. manually import obj files to blender in a batch

B:
OBJ to new format txt:: command options are  -blenderTool -of new_txt
find all the obj files in the input directory and convert to txt in the output directory

C:
TXT to MOD format :: command options are  -blenderTool -of old
find all the txt files in the input directory and convert to mod in the output directory

I suppose that B and C could be combined in one step to make it easier,but maybe later when I include the blender headless python code to input the models and action scripting to do armatures and RK ( reverse kinematics ) on the models and export it back as scripts or C++ code modules.

EXAMPLES:
python converter.py -blenderTool -di models-new -do blender_obj -image -of obj
python converter.py -blenderTool -di blender_obj -do newtxt -image -of new_txt
python converter.py -blenderTool -di newtxt -do newmod -image -of old

'''
def convertEach():
    #command to create a reference image for model
    #blender HumanTorso1v.blend -b -o orso -F PNG  -f 1
    print "convert here"

# convert file
if batch_mode:
    modelformat.convert_list(file_list, in_format, in_params, out_format, out_params)
elif dir_mode:
    if out_format == "obj":
        print "This is TXT to OBJ -- input dir = ",in_dir," out dir is ",out_dir,\
            " out format is ",out_format," in format is ",in_format," get images is ",image_mode
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for root,dirs,files in os.walk(join(".",in_dir),topdown=False):
            for name in files:
                print name
                base_name=name.split('.')[0]
                os.chdir(in_dir) #Needs to be in that dir so mtl file relative is .\
                modelformat.convert(in_format, join("..",in_dir,name), in_params, out_format, \
                join(base_name+".obj"), out_params)
                os.chdir("..")
                shutil.move(join(in_dir,base_name+".obj"),join(out_dir,base_name+".obj"))
                shutil.move(join(in_dir,base_name+".mtl"),join(out_dir,base_name+".mtl"))
                for i,line in enumerate(open(join(".",out_dir,base_name+".mtl"))):
                    for match in re.finditer(pattern,line):
                        image_name=line.split(image_code)[1]
                        image_name=image_name.strip()
                        print "adding ",image_name," to obj file dir"
                        if not os.path.exists("./"+out_dir+"/"+image_name):
                            for root2,dirs2,files2 in os.walk(join("..","."),topdown=False):
                                for name2 in files2:
                                    if name2==image_name:
                                        print "Moving this ",join(root2, name2)
                                        copyfile(join(root2,name2),join(".",out_dir,image_name))
                                        img = Image.open(join(".",out_dir,image_name)).transpose(Image.FLIP_TOP_BOTTOM)
                                        img.save(join(".",out_dir,image_name))
    if out_format == "new_txt":
        print "This is OBJ to TXT -- input dir = ",in_dir," out dir is ",out_dir,\
            " out format is ",out_format," in format is ",in_format," get images is ",image_mode
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for root,dirs,files in os.walk(join(".",in_dir),topdown=False):
            for name in files:
                print name
                if ".obj" in name:
                    base_name=name.split('.')[0]
                    print join(".",in_dir,name)
                    os.chdir(in_dir) #Needs to be in that dir so model format can find the .mtl file
                    modelformat.convert(in_format, join(name), in_params, out_format, \
                    join("..",".",out_dir,base_name+".txt"), out_params)
                    os.chdir("..")
    if out_format == "old":
        print "This is TXT to MOD -- input dir = ",in_dir," out dir is ",out_dir,\
            " out format is ",out_format," in format is ",in_format," get images is ",image_mode
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        print join(".",in_dir)
        for root,dirs,files in os.walk(join(".",in_dir),topdown=False):
            for name in files:
                print name
                if ".txt" in name:
                    base_name=name.split('.')[0]
                    modelformat.convert(in_format, join(".",in_dir,name), in_params, out_format, \
                    join(".",out_dir,base_name+".mod"), out_params)
    exit()
else:
    if (in_filename != None) and (out_filename != None):
        if os.path.isfile(in_filename):
            modelformat.convert(in_format, in_filename, in_params, out_format, out_filename, out_params)
        else:
            print'No such input file ->',in_filename
    else:
        if (in_filename == None):
            print 'Missing input source file name ->',in_filename
            print 'Example: \"python converter.py -i fileToConvert.ext -o newFormatFile.ext\"'
        if (out_filename == None):
            print 'Missing destination file name ->',in_filename
            print 'Example: \"python converter.py -i fileToConvert.ext -o newFormatFile.ext\"'
