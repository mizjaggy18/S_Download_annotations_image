# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2018. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.


__author__ = "WSH Munirah W Ahmad <wshmunirah@gmail.com>"
__copyright__ = "Apache 2 license. Made by Multimedia University Cytomine Team, Cyberjaya, Malaysia, http://cytomine.mmu.edu.my/"
__version__ = "1.0.0"

import os
import logging
import sys
import shutil

import cytomine
from cytomine.models import Property, Annotation, AnnotationTerm, AnnotationCollection, JobData, Job, TermCollection, ImageInstanceCollection


# Date created: 14 December 2021

def run(cyto_job, parameters):
    logging.info("----- Download annotations image v%s -----", __version__)
    logging.info("Entering run(cyto_job=%s, parameters=%s)", cyto_job, parameters)

    job = cyto_job.job
    user = job.userJob
    project = cyto_job.project
    download_option=parameters.cytomine_id_download

    terms = TermCollection().fetch_with_filter("project", project.id)
    print(terms)

    # start_time=time.time()

    #Select images to process
    images = ImageInstanceCollection().fetch_with_filter("project", project.id)

    list_imgs = []
    if parameters.cytomine_id_images == 'all':
        for image in images:
            list_imgs.append(int(image.id))
    else:
        list_imgs = parameters.cytomine_id_images
        list_imgs2 = list_imgs.split(',')
    
    print('Input param:', parameters.cytomine_id_images)
    print('Print list images:', list_imgs2)  

    list_terms = []
    if parameters.cytomine_id_terms == 'all':
        for term in terms:
            list_terms.append(int(term.id))
    else:
        list_terms = parameters.cytomine_id_terms
        list_terms2 = list_terms.split(',')
    
    print('Input param:', parameters.cytomine_id_terms)
    print('Print list terms:', list_terms2)


    # I create a working directory that I will delete at the end of this run
    working_path = os.path.join("tmp", str(job.id))
    if not os.path.exists(working_path):
        logging.info("Creating working directory: %s", working_path)
        os.makedirs(working_path)
    try:
        
        for id_image in list_imgs2:
            print('Current image:', id_image)

            for id_term in list_terms2:
                print('Current term:', id_term)

                id_project=project.id
                            
                annotations = AnnotationCollection()        
                annotations.project = id_project
                annotations.image = id_image
                annotations.term = id_term
                annotations.showWKT = True


                if parameters.cytomine_id_user_job != 0:
                    annotations.job = parameters.cytomine_id_annotation_job
                    annotations.user = parameters.cytomine_id_user_job

                annotations.fetch()
                print(annotations)

                # nb_annotations=len(annotations)
                logging.info("Downloading annotations...")
                job.update(progress=80, statusComment="Downloading annotations...")
                # progress = 0
                # progress_delta = 100 / nb_annotations

                output_path = os.path.join(working_path, "annotations_images.zip")
                # f= open(output_path,"w+")
                # f.write("ID;Image;Project;JobID;Term;User;Area;Perimeter;WKT \n")

                for annotation in annotations:                    
                    # progress += progress_delta
                    # f.write("{};{};{};{};{};{};{};{};{}\n".format(annotation.id,annotation.image,annotation.project,annotations.job,annotation.term,annotation.user,annotation.area,annotation.perimeter,annotation.location))
                    if download_option==1: #crop
                        annotation.dump(dest_pattern=os.path.join(working_path, "crop", "{id}.png"))
                    elif download_option==2: #alpha
                        annotation.dump(dest_pattern=os.path.join(working_path, "alpha", "{id}.png"), mask=True)
                    elif download_option==3: #crop,alpha,mask
                        annotation.dump(dest_pattern=os.path.join(working_path, "crop", "{id}.png"))
                        annotation.dump(dest_pattern=os.path.join(working_path, "alpha", "{id}.png"), mask=True)
                        annotation.dump(dest_pattern=os.path.join(working_path, "mask", "{id}.png"), mask=True, alpha=True)

        # f.close()   
            
        #I save a file generated by this run into a "job data" that will be available in the UI. 
        shutil.make_archive("annotations_images", 'zip', working_path)
        job_data = JobData(job.id, "Generated File", "annotations_images.zip").save()
        job_data.upload("annotations_images.zip")
        job.update(progress=100, statusComment="Annotations saved!")
                

    finally:
#         logging.info("Deleting folder %s", working_path)
#         shutil.rmtree(working_path, ignore_errors=True)
        logging.debug("Leaving run()")


if __name__ == "__main__":
    logging.debug("Command: %s", sys.argv)

    with cytomine.CytomineJob.from_cli(sys.argv) as cyto_job:
        run(cyto_job, cyto_job.parameters)


