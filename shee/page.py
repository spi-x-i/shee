#!/usr/bin/env python
# -*- coding: utf-8 -*

import os

import webbrowser


class WebObject(object):
    def __init__(self):
        self.filename = ""
        self.dirname = ""
        self.path = {}

    def set_filename(self, filename):
        self.filename = filename

    def set_dirname(self, dirname):
        self.dirname = dirname

    def set_pathtree(self, path):
        self.path = self._recursive_set(path)

    def _recursive_set(self, path):
        d = {'name': os.path.basename(path)}
        if os.path.isdir(path):
            d['type'] = "directory"
            d['children'] = [self._recursive_set(os.path.join(path,x)) for x in os.listdir(path)]
        else:
            d['type'] = "file"
        return d

    def _get_fullname(self):
        return self.dirname + '/' + self.filename

    def _get_main_name(self):
        return self._get_fullname() + '.html'

    def _get_cpu_name(self, exp):
        return self._get_fullname() + '-cpu' + str(exp) + '.html'

    def _get_disk_name(self, exp):
        return self._get_fullname() + '-dsk' + str(exp) + '.html'

    def _get_eth_name(self, exp):
        return self._get_fullname() + '-eth' + str(exp) + '.html'

    def _get_aggr_name(self, exp=''):
        return self._get_fullname() + '-agg' + str(exp) + '.html'

    def page(self):
        f = open(self._get_main_name(), 'w')
        d = self.path

        message = """<!DOCTYPE html><html>
        <head>
        <style>
        #myImg {
            border-radius: 5px;
            cursor: pointer;
            transition: 0.3s;
        }

        #myImg:hover {opacity: 0.7;}

        /* The Modal (background) */
        .modal {
            display: none; /* Hidden by default */
            position: fixed; /* Stay in place */
            z-index: 1; /* Sit on top */
            padding-top: 100px; /* Location of the box */
            left: 0;
            top: 0;
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            overflow: auto; /* Enable scroll if needed */
            background-color: rgb(0,0,0); /* Fallback color */
            background-color: rgba(0,0,0,0.9); /* Black w/ opacity */
        }

        /* Modal Content (Image) */
        .modal-content {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
        }

        /* Caption of Modal Image (Image Text) - Same Width as the Image */
        #caption {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
            text-align: center;
            color: #ccc;
            padding: 10px 0;
            height: 150px;
        }

        /* Add Animation - Zoom in the Modal */
        .modal-content, #caption {
            -webkit-animation-name: zoom;
            -webkit-animation-duration: 0.6s;
            animation-name: zoom;
            animation-duration: 0.6s;
        }

        @-webkit-keyframes zoom {
            from {-webkit-transform:scale(0)}
            to {-webkit-transform:scale(1)}
        }

        @keyframes zoom {
            from {transform:scale(0)}
            to {transform:scale(1)}
        }

        /* The Close Button */
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
        }

        .close:hover,
        .close:focus {
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }

        /* 100% Image Width on Smaller Screens */
        @media only screen and (max-width: 700px){
            .modal-content {
                width: 100%;
            }
        }

        #quotescointainer{
        width: 100%;
        height: auto;
        font-size: 12px;
        overflow: hidden; /* contain floated elements */
        background: #ccc
        }
        #quotes0 {
            float: left;
            width: 25%;
        }
        #quotes1 {
            float: left;
            width: 25%;
        }
        #quotes2 {
            float: left;
            width: 25%;
        }
        #quotes3 {
            float: left;
            width: 25%;
        }
        img {width:300px; height:auto;}
        </style>
        </head>
        <body>
        <h1>dstat-shee: a simple Data Visualization Tool</h1>
        """
        message += '<br><a href="' + self._get_aggr_name() + ' ">go to aggregation results</a><br>'

        basedir = os.path.join(self.dirname, os.pardir)

        img_counter = 0
        for item in d['children']:  # for each main directory dstat-hadoop-cloud . . .
            if item['type'] == 'directory' and item['name'] == 'aggregation':
                self._create_aggregation_page(basedir=os.path.join(basedir, item['name']))
            if item['type'] == 'directory' and item['name'] != 'html' and item['name'] != 'aggregation':
                message += "<h3>" + item['name'] + "</h3>"
                expdir = os.path.join(basedir, item['name'])
                message += '<div id="quotescontainer">'
                for idx, device in enumerate(item['children']):  # for each device i.e. cpu, network, memory<!DOCTYPE html>

                    if device['type'] == 'directory':
                        devicedir = os.path.join(expdir, device['name'])

                        for image in device['children']: # for each image inside the device dir
                            if image['type'] == 'directory' and image['name'].startswith('cpu'):
                                self._create_cpu_page(devicedir, item['name'].split("-")[-1])
                            elif image['type'] == 'directory' and image['name'].startswith('eth'):
                                # self._create_eth_page(devicedir, item['name'].split("-")[-1])
                                pass
                            elif image['type'] == 'directory' and image['name'].startswith('sd'):
                                self._create_disk_page(devicedir, item['name'].split("-")[-1])
                            if image['type'] == 'file' and image['name'].endswith('stacked.png'):
                                message += '<div id="quotes' + str(idx) + '">'
                                message += "<h5>" + device['name'] + "</h5>"
                                src = 'file://' + os.path.join(devicedir, image['name'])
                                message += '<img id="myImg' + str(img_counter) + '" src="' + src + '">'
                                if device['name'] == 'cpu':
                                    message += '<br><a href="' + self._get_cpu_name(item['name'].split("-")[-1]) + ' ">go to nodes page</a>'
                                elif device['name'] == 'disk':
                                    message += '<br><a href="' + self._get_disk_name(item['name'].split("-")[-1]) + ' ">go to disks page</a>'
                                message += '</div>'
                                img_counter += 1
                message += "</div>"
                message += '<hr style="clear: both;">'

        message += '''
        <!-- The Modal -->
        <div id="myModal" class="modal">

          <!-- The Close Button -->
          <span class="close" onclick="document.getElementById('myModal').style.display='none'">&times;</span>

          <!-- Modal Content (The Image) -->
          <img class="modal-content" id="img01">

          <!-- Modal Caption (Image Text) -->
          <div id="caption"></div>
        </div>
        '''
        message += '''<script>
        // Get the modal
        var modal = document.getElementById('myModal');

        // Get the image and insert it inside the modal - use its "alt" text as a caption
        var modalImg = document.getElementById("img01");
        var captionText = document.getElementById("caption");'''
        for n in range(0,img_counter):
            message += '''
            var img''' + str(n) + ''' = document.getElementById('myImg''' + str(n) + '''');
            img''' + str(n) + '''.onclick = function(){
                modal.style.display = "block";
                modalImg.src = this.src;
                modalImg.alt = this.alt;
                captionText.innerHTML = this.alt;
            }'''
        message += '''
        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];

        // When the user clicks on <span> (x), close the modal
        span.onclick = function() {
          modal.style.display = "none";
        }
        </script>'''
        message += """
        </body>
        </html>"""

        f.write(message)
        f.close()

        # change path to reflect file location
        filepath = "file://" + self._get_main_name()
        webbrowser.open_new_tab(filepath)

        return

    def _create_cpu_page(self, basedir, exp):
        # base directory arriva a ...../cpu
        f = open(self._get_cpu_name(exp), 'w')
        d = self._recursive_set(basedir)
        message = '''<!DOCTYPE html><html>
        <head>
        <style>
        #myImg {
            border-radius: 5px;
            cursor: pointer;
            transition: 0.3s;
        }

        #myImg:hover {opacity: 0.7;}

        /* The Modal (background) */
        .modal {
            display: none; /* Hidden by default */
            position: fixed; /* Stay in place */
            z-index: 1; /* Sit on top */
            padding-top: 100px; /* Location of the box */
            left: 0;
            top: 0;
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            overflow: auto; /* Enable scroll if needed */
            background-color: rgb(0,0,0); /* Fallback color */
            background-color: rgba(0,0,0,0.9); /* Black w/ opacity */
        }

        /* Modal Content (Image) */
        .modal-content {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
        }

        /* Caption of Modal Image (Image Text) - Same Width as the Image */
        #caption {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
            text-align: center;
            color: #ccc;
            padding: 10px 0;
            height: 150px;
        }

        /* Add Animation - Zoom in the Modal */
        .modal-content, #caption {
            -webkit-animation-name: zoom;
            -webkit-animation-duration: 0.6s;
            animation-name: zoom;
            animation-duration: 0.6s;
        }

        @-webkit-keyframes zoom {
            from {-webkit-transform:scale(0)}
            to {-webkit-transform:scale(1)}
        }

        @keyframes zoom {
            from {transform:scale(0)}
            to {transform:scale(1)}
        }

        /* The Close Button */
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
        }

        .close:hover,
        .close:focus {
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }

        /* 100% Image Width on Smaller Screens */
        @media only screen and (max-width: 700px){
            .modal-content {
                width: 100%;
            }
        }

        #quotescointainer{
        width: 100%;
        font-size: 12px;
        overflow: hidden; /* contain floated elements */
        background: #ccc
        }
        #quotes0 {
            float: left;
            width: 33%;
            clear: both;
        }
        #quotes1 {
            float: left;
            width: 33%;
        }
        #quotes2 {
            float: left;
            width: 33%;
        }
        img {width:400px; height:auto;}
        </style>
        </head>
        <body>
        <h1>dstat-shee: a simple Data Visualization Tool</h1>
        <a href="''' + self._get_main_name() + '''">back to main page</a>
        <br>
        '''
        img_counter = 0
        quote_counter = 0
        message += '<div id="quotescontainer">'
        for item in d['children']:
            if quote_counter > 2:
                quote_counter = 0
                message += '</div>'
                message += '<div id="quotescontainer">'
            if item['type'] == 'directory' and item['name'].startswith('cpu'):

                for subdevice in item['children']:  # for each file in cpux

                    if subdevice['type'] == 'file' and subdevice['name'].endswith('stacked.png'):
                        subdevice_dir = os.path.join(basedir, item['name'])
                        message += '<div id="quotes' + str(quote_counter) + '">'
                        message+= "<h3>" + item['name'] + "</h3>"
                        quote_counter += 1
                        message += "<h5>" + subdevice['name'] + "</h5>"
                        src = 'file://' + os.path.join(subdevice_dir, subdevice['name'])
                        message += '<img id="myImg' + str(img_counter) + '" src="' + src + '">'
                        message += '</div>'
                        img_counter += 1
                        break
        message += '</div>'

        message += '''
        <!-- The Modal -->
        <div id="myModal" class="modal">

          <!-- The Close Button -->
          <span class="close" onclick="document.getElementById('myModal').style.display='none'">&times;</span>

          <!-- Modal Content (The Image) -->
          <img class="modal-content" id="img01">

          <!-- Modal Caption (Image Text) -->
          <div id="caption"></div>
        </div>
        '''
        message += '''<script>
        // Get the modal
        var modal = document.getElementById('myModal');

        // Get the image and insert it inside the modal - use its "alt" text as a caption
        var modalImg = document.getElementById("img01");
        var captionText = document.getElementById("caption");'''
        for n in range(0,img_counter):
            message += '''
            var img''' + str(n) + ''' = document.getElementById('myImg''' + str(n) + '''');
            img''' + str(n) + '''.onclick = function(){
                modal.style.display = "block";
                modalImg.src = this.src;
                modalImg.alt = this.alt;
                captionText.innerHTML = this.alt;
            }'''
        message += '''
        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];

        // When the user clicks on <span> (x), close the modal
        span.onclick = function() {
          modal.style.display = "none";
        }
        </script>'''
        message += """
        </body>
        </html>"""

        f.write(message)
        f.close()

        return

    def _create_disk_page(self, basedir, exp):
        # base directory arriva a ...../disk
        f = open(self._get_disk_name(exp), 'w')
        d = self._recursive_set(basedir)
        message = '''<!DOCTYPE html><html>
        <head>
        <style>
        #myImg {
            border-radius: 5px;
            cursor: pointer;
            transition: 0.3s;
        }

        #myImg:hover {opacity: 0.7;}

        /* The Modal (background) */
        .modal {
            display: none; /* Hidden by default */
            position: fixed; /* Stay in place */
            z-index: 1; /* Sit on top */
            padding-top: 100px; /* Location of the box */
            left: 0;
            top: 0;
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            overflow: auto; /* Enable scroll if needed */
            background-color: rgb(0,0,0); /* Fallback color */
            background-color: rgba(0,0,0,0.9); /* Black w/ opacity */
        }

        /* Modal Content (Image) */
        .modal-content {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
        }

        /* Caption of Modal Image (Image Text) - Same Width as the Image */
        #caption {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
            text-align: center;
            color: #ccc;
            padding: 10px 0;
            height: 150px;
        }

        /* Add Animation - Zoom in the Modal */
        .modal-content, #caption {
            -webkit-animation-name: zoom;
            -webkit-animation-duration: 0.6s;
            animation-name: zoom;
            animation-duration: 0.6s;
        }

        @-webkit-keyframes zoom {
            from {-webkit-transform:scale(0)}
            to {-webkit-transform:scale(1)}
        }

        @keyframes zoom {
            from {transform:scale(0)}
            to {transform:scale(1)}
        }

        /* The Close Button */
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
        }

        .close:hover,
        .close:focus {
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }

        /* 100% Image Width on Smaller Screens */
        @media only screen and (max-width: 700px){
            .modal-content {
                width: 100%;
            }
        }

        #quotescointainer{
        width: 100%;
        font-size: 12px;
        overflow: hidden; /* contain floated elements */
        background: #ccc;
        }
        #quotes0 {
            float: left;
            width: 33%;
            clear: both;
        }
        #quotes1 {
            float: left;
            width: 33%;
        }
        #quotes2 {
            float: left;
            width: 33%;
        }
        img {width:400px; height:auto;}
        </style>
        </head>
        <body>
        <h1>dstat-shee: a simple Data Visualization Tool</h1>
        <a href="''' + self._get_main_name() + '''">back to main page</a>
        <br>
        '''
        img_counter = 0
        quote_counter = 0
        message += '<div id="quotescontainer">'
        for item in d['children']:
            if quote_counter > 2:
                quote_counter = 0
                message += '</div>'
                message += '<div id="quotescontainer">'
            if item['type'] == 'directory' and item['name'].startswith('sd'):

                for subdevice in item['children']:  # for each file in cpux

                    if subdevice['type'] == 'file' and subdevice['name'].endswith('stacked.png'):
                        subdevice_dir = os.path.join(basedir, item['name'])
                        message += '<div id="quotes' + str(quote_counter) + '">'
                        message+= "<h3>" + item['name'] + "</h3>"
                        quote_counter += 1
                        message += "<h5>" + subdevice['name'] + "</h5>"
                        src = 'file://' + os.path.join(subdevice_dir, subdevice['name'])
                        message += '<img id="myImg' + str(img_counter) + '" src="' + src + '">'
                        message += '</div>'
                        img_counter += 1
                        break
        if quote_counter <= 2:
            while quote_counter <= 2:
                message += '<div id="quotes' + str(quote_counter) + '"></div>'
                quote_counter += 1
        message += '</div>'

        message += '''
        <!-- The Modal -->
        <div id="myModal" class="modal">

          <!-- The Close Button -->
          <span class="close" onclick="document.getElementById('myModal').style.display='none'">&times;</span>

          <!-- Modal Content (The Image) -->
          <img class="modal-content" id="img01">

          <!-- Modal Caption (Image Text) -->
          <div id="caption"></div>
        </div>
        '''
        message += '''<script>
        // Get the modal
        var modal = document.getElementById('myModal');

        // Get the image and insert it inside the modal - use its "alt" text as a caption
        var modalImg = document.getElementById("img01");
        var captionText = document.getElementById("caption");'''
        for n in range(0,img_counter):
            message += '''
            var img''' + str(n) + ''' = document.getElementById('myImg''' + str(n) + '''');
            img''' + str(n) + '''.onclick = function(){
                modal.style.display = "block";
                modalImg.src = this.src;
                modalImg.alt = this.alt;
                captionText.innerHTML = this.alt;
            }'''
        message += '''
        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];

        // When the user clicks on <span> (x), close the modal
        span.onclick = function() {
          modal.style.display = "none";
        }
        </script>'''
        message += """
        </body>
        </html>"""

        f.write(message)
        f.close()

        return

    def _create_aggregation_page(self, basedir, exp=''):
        # base directory arriva a ...../cpu
        f = open(self._get_aggr_name(exp), 'w')
        d = self._recursive_set(basedir)
        message = '''<!DOCTYPE html><html>
        <head>
        <style>
        #myImg {
            border-radius: 5px;
            cursor: pointer;
            transition: 0.3s;
        }

        #myImg:hover {opacity: 0.7;}

        /* The Modal (background) */
        .modal {
            display: none; /* Hidden by default */
            position: fixed; /* Stay in place */
            z-index: 1; /* Sit on top */
            padding-top: 100px; /* Location of the box */
            left: 0;
            top: 0;
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            overflow: auto; /* Enable scroll if needed */
            background-color: rgb(0,0,0); /* Fallback color */
            background-color: rgba(0,0,0,0.9); /* Black w/ opacity */
        }

        /* Modal Content (Image) */
        .modal-content {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
        }

        /* Caption of Modal Image (Image Text) - Same Width as the Image */
        #caption {
            margin: auto;
            display: block;
            width: 80%;
            max-width: 700px;
            text-align: center;
            color: #ccc;
            padding: 10px 0;
            height: 150px;
        }

        /* Add Animation - Zoom in the Modal */
        .modal-content, #caption {
            -webkit-animation-name: zoom;
            -webkit-animation-duration: 0.6s;
            animation-name: zoom;
            animation-duration: 0.6s;
        }

        @-webkit-keyframes zoom {
            from {-webkit-transform:scale(0)}
            to {-webkit-transform:scale(1)}
        }

        @keyframes zoom {
            from {transform:scale(0)}
            to {transform:scale(1)}
        }

        /* The Close Button */
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
        }

        .close:hover,
        .close:focus {
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }

        /* 100% Image Width on Smaller Screens */
        @media only screen and (max-width: 700px){
            .modal-content {
                width: 100%;
            }
        }

        #quotescointainer{
        width: 100%;
        font-size: 12px;
        overflow: hidden; /* contain floated elements */
        background: #ccc;
        }
        #quotes0 {
            float: left;
            width: 33%;
            clear: both;
        }
        #quotes1 {
            float: left;
            width: 33%;
        }
        #quotes2 {
            float: left;
            width: 33%;
        }
        img {width:400px; height:auto;}
        </style>
        </head>
        <body>
        <h1>dstat-shee: a simple Data Visualization Tool</h1>
        <a href="''' + self._get_main_name() + '''">back to main page</a>
        <br>
        '''
        img_counter = 0
        quote_counter = 0

        for item in d['children']:  # stuffs inside aggregation directory
            if item['type'] == 'directory':
                message += '<br style="clear:both"><h3>' + item['name'] + '</h3>'
                message += '<div id="quotescontainer">'
                device_dir = os.path.join(basedir, item['name'])
                for device in item['children']:  # here images for each device

                    if quote_counter > 2:
                        quote_counter = 0
                        message += '</div>'
                        message += '<div id="quotescontainer">'

                    message += '<div id="quotes' + str(quote_counter) + '">'
                    quote_counter += 1
                    message += "<h5>" + device['name'].split('-')[-1].split('.')[0] + "</h5>"
                    src = 'file://' + os.path.join(device_dir, device['name'])
                    message += '<img id="myImg' + str(img_counter) + '" src="' + src + '">'
                    message += '</div>'
                    img_counter += 1
                if quote_counter <= 2:
                    while (quote_counter <= 2):
                        message += '<div id="quotes' + str(quote_counter) + '"></div>'
                        quote_counter += 1
                    quote_counter = 0
                    message += '</div>'
        message += '</div>'

        message += '''
        <!-- The Modal -->
        <div id="myModal" class="modal">

          <!-- The Close Button -->
          <span class="close" onclick="document.getElementById('myModal').style.display='none'">&times;</span>

          <!-- Modal Content (The Image) -->
          <img class="modal-content" id="img01">

          <!-- Modal Caption (Image Text) -->
          <div id="caption"></div>
        </div>
        '''
        message += '''<script>
        // Get the modal
        var modal = document.getElementById('myModal');

        // Get the image and insert it inside the modal - use its "alt" text as a caption
        var modalImg = document.getElementById("img01");
        var captionText = document.getElementById("caption");'''
        for n in range(0, img_counter):
            message += '''
            var img''' + str(n) + ''' = document.getElementById('myImg''' + str(n) + '''');
            img''' + str(n) + '''.onclick = function(){
                modal.style.display = "block";
                modalImg.src = this.src;
                modalImg.alt = this.alt;
                captionText.innerHTML = this.alt;
            }'''
        message += '''
        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];

        // When the user clicks on <span> (x), close the modal
        span.onclick = function() {
          modal.style.display = "none";
        }
        </script>'''
        message += """
        </body>
        </html>"""

        f.write(message)
        f.close()

        return