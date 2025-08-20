from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import os
import json
from google.protobuf.json_format import MessageToJson, MessageToDict
import yaml
import datetime
from pdf2image import convert_from_path
import pytesseract
from operator import itemgetter
import loggerutility as logger
from PIL import Image, ImageOps


class GenerateExtractTemplate:

    def generateTemplate(self,project_id: str, location: str, processor_id: str, file_path: str, mime_type: str, yml_file_path: str):
        document_json_path = 'document_ai.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = document_json_path
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts, )
        name = client.processor_path(project_id, location, processor_id)

        with open(file_path, "rb") as image:
            image_content = image.read()
        
        raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        document = result.document.entities
        images = convert_from_path(file_path)
        for i in range(len(images)):
            images[i].save('page' + str(i) + '.jpg', 'JPEG')

        global img, yml_file_name, invoice_name, endvalue
        img = Image.open(r"page0.jpg")
        img1 = Image.open('page' + str(len(images) - 1) + '.jpg')
        width = img.width
        height = img.height
        line = 0
        
        line_item_points = []
        
        lenthofjson = len(document)

        for num, data in enumerate(document):
            line_item_regex = ""
            if lenthofjson - 1 == num:
                propertyvalues = data.properties
                
                for values in propertyvalues:
                    value = values.page_anchor.page_refs
                    for indexvalue in value:
                        l = []
                        l.append(int(indexvalue.bounding_poly.normalized_vertices[0].x * width))
                        l.append(int(indexvalue.bounding_poly.normalized_vertices[0].y * height))
                        l.append(int(indexvalue.bounding_poly.normalized_vertices[2].x * width))
                        l.append(int(indexvalue.bounding_poly.normalized_vertices[2].y * height))
                        img1 = img1.crop((0, l[3], l[2], l[3] + 120))
                        OCR = pytesseract.image_to_string(img1)
                        OCR = OCR.strip()
                        Last_value = OCR.split()
                        endvalue = ''
                        for intvalue ,lastvalue in enumerate(Last_value):
                            endvalue = endvalue + lastvalue + ' '
                        break

            if data.type_ == 'supplier_name':
                invoice_name = (data.mention_text).strip()
                # print('invoice_name',invoice_name)
                supplier_name = invoice_name.split()
                yml_file_name = supplier_name[0]

            elif data.type_ == 'receiver_name':
                invoice_name = (data.mention_text).strip()
                # print('invoice_name',invoice_name)
                supplier_name = invoice_name.split()
                yml_file_name = supplier_name[0]

            if data.type_ == 'line_item' and line<5:
                line = line + 1
                line_item_points = []
                valuelist = []
                k = data.properties
                for p in k:
                    # print(' !!!!!!!!!!!!!!!!! 83', p)
                    label = (p.type_).split("/")
                    if label[1] not in valuelist:
                        valuelist.append(label[1])
                        m = p.page_anchor.page_refs
                        for i in m:
                            l = []
                            l.append(int(i.bounding_poly.normalized_vertices[0].x * width))
                            l.append(int(i.bounding_poly.normalized_vertices[0].y * height))
                            l.append(int(i.bounding_poly.normalized_vertices[2].x * width))
                            l.append(int(i.bounding_poly.normalized_vertices[2].y * height))
                            l.append(label[1])
                            l.append(int(i.bounding_poly.normalized_vertices[1].x * width))
                            l.append(int(i.bounding_poly.normalized_vertices[1].y * height))
                            l.append(int(i.bounding_poly.normalized_vertices[3].x * width))
                            l.append(int(i.bounding_poly.normalized_vertices[3].y * height))
                            line_item_points.append(l)
                # try:
                    # logger.log(f"line_item_points !!!!! 98 : {line_item_points}","0")
                line_item = self.generateLineTemplate(line_item_points)
                # except Exception as ex:
                #     logger.log(f"Google cloud : Exception while creating line item regex  {ex}","0")
                
                # if line == '0':
                #     line_item_regex = line_item
                #     print('line_item_regex !!!!!!!!!!!!! 107',line_item_regex)
                if line_item.count('?') > line_item_regex.count("?") and line != '0':
                    line_item_regex = line_item
                    # print('line_item_regex !!!!!!!!!!!!!! 104',line_item_regex)

        na = []
        for k, vv in enumerate(str(yml_file_name)):
            if k < 2:
                na.append(vv)
            else:
                break

        code = '00000001'
        valueofwhitespace = False
        startvalues = "" + str(startvalue)
        linevalue = self.line_item_regex
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'document_ai.json'
        opts = ClientOptions(api_endpoint=f"{'us'}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts, )
        name = client.processor_path('document-ai-370906', 'us', 'f057e94c15eb5161')
        with open(file_path, "rb") as image:
            image_content = image.read()

        raw_document = documentai.RawDocument(content=image_content, mime_type='application/pdf')
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request)
        document = result
        headervalues = []
        datavalue = []
        for page in document.document.pages:
            for va in page.form_fields:
                if va.field_name.text_anchor.content.strip().endswith(":"):
                    headervalues.append(va.field_name.text_anchor.content.strip())
                    datavalue.append(va.field_value.text_anchor.content.strip())

        f = open(yml_file_path+'/'+str(yml_file_name).capitalize() + ".yml", "x")
        dict_file = dict(
            issuer=str(invoice_name),
            keywords=[str(invoice_name)],
            fields=dict(static_cust_code=na[0] + na[1] + code,
                        ),
            options=dict(remove_whitespace=valueofwhitespace),
            required_fields=[],
            lines=dict(
                start=str(startvalues),
                end=endvalue,
                line=linevalue,
            )
        )
        for k, i in enumerate(headervalues):
            if i.endswith(":") is True and i[:-2] != '\n':
                fields_value = i.replace(':', "").strip().replace("\n", "").replace(" ", "_")
                assign_value = i.strip().replace("\n", "")
                if assign_value.replace(':', ""):
                    dict_file['fields'][fields_value] = assign_value + '\s*(\S+)'
                else:
                    dict_file['fields'][fields_value] = assign_value + '\s*(\S+)'

        for i in headervalues:
            if i.endswith(":") is True and i[:-2] != '\n':
                dict_file['required_fields'] = [i.replace(':', "").strip().replace("\n", "").replace(" ", "_")]
            break

        with open(yml_file_path+'/'+str(yml_file_name).capitalize() + '.yml', 'w') as file:
            documents = yaml.dump(dict_file, file, default_flow_style=False)


    def generateHeaderTemplate(self,ymlfilepath: str, ent_names: str, ent_codes: str, ent_types: str,ai_proc_variables:str, OCR_Text:str, template_Keyword_1:str, template_Keyword_2:str):

        ymlfilepath = ymlfilepath

        if isinstance(ai_proc_variables, str):
            ai_proc_variables = json.loads(ai_proc_variables)
        logger.log(f"template_Keyword_1::186  {template_Keyword_1}")
        logger.log(f"template_Keyword_2::187  {template_Keyword_2}")

        logger.log(f"ymlfilepath : {ymlfilepath}","0")
        f = open(ymlfilepath, "x")
        dict_file = dict(
            issuer=str(ent_names),
            keywords=[str(ent_names)] + [str(keyword) for keyword in [template_Keyword_1, template_Keyword_2] if keyword],
            fields=dict(static_ent_code=ent_codes,
                        static_ent_name=ent_names,
                        static_ent_type=ent_types,
                        order_dt=dict(
                            pattern='Order Date\s+:\s*\s(\d{1,2}\/\d{1,2}\/\d{4})',
                            required=False,
                            )
                        ),
            options=dict(remove_whitespace=False),
            required_fields=[]
            )
        for val in ai_proc_variables["Details"]:
            if val['mandatory'] == 'true':
                if (val['displayName']).strip():
                    # dict_file['fields'][val['name']] = val['displayName'] + '( |.|)(:|::|)( |)\s*\s(\S*)'
                    dict_file['fields'][val['name']] = val['displayName'] + '\s*\s(\S*)'
                else:
                    headerValue = self.getHeaderLabel(OCR_Text = OCR_Text,value = val['defaultValue'])
                    # dict_file['fields'][val['name']] = headerValue + '( |.|)(:|::|)( |)\s*\s(\S*)'
                    dict_file['fields'][val['name']] = headerValue + '\s*\s(\S*)'
                # mandatory.append(val['name'])

        # for mandatory_value in mandatory:
        #     dict_file['fields'][mandatory_value] = mandatory_value + '( |.|)(:|::|)( |)\s*\s(\S*)'
        if len(dict_file) != 0:
            with open(ymlfilepath, 'w') as file:
                logger.log(f'\n[ Template created 214  :          {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
                documents = yaml.dump(dict_file, file, default_flow_style=False)

    def generateOCRTextFile(self,ocrfilepath: str, ent_names: str, ent_codes: str, ent_types: str,ai_proc_variables:str, OCR_Text:str, template_Keyword_1:str, template_Keyword_2:str):

        logger.log(f"generateOCRTextFile ocrfilepath :: {ocrfilepath}")

        if len(OCR_Text) != 0:
            with open(ocrfilepath, 'w') as file:
                logger.log(f'\n OCRFilepath created 214  :          {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
                file.write(OCR_Text)

    def generateLineTemplate(self,L):
        global startvalue
        rege = ''
        blankspace = 0
        sorted_list = sorted(L, key=itemgetter(0))
        logger.log(f"line_item_points !!!!! 201 : {sorted_list}","0")
        for s in range(len(sorted_list)):
            if s == 0:
                Tempval = img.crop((sorted_list[s][0] - 200, sorted_list[s][1] - 150, sorted_list[s][5], sorted_list[s][6]))
                image1 = img.crop((sorted_list[s][0] - 50, sorted_list[s][1] - 5, sorted_list[s][2], sorted_list[s][3]))
                image = img.crop((sorted_list[s][0], sorted_list[s][1] - 5, sorted_list[s][2], sorted_list[s][3]))

                Tempval = pytesseract.image_to_string(Tempval)
                OCR1 = pytesseract.image_to_string(image1)
                OCR = pytesseract.image_to_string(image)

                Tempval = Tempval.strip()
                OCR1 = OCR1.strip()
                OCR = OCR.strip()
                startvalues = Tempval.split()
                startvalue = startvalues[0]
                k = OCR1.replace(OCR, '')

                val = k.strip()
                if val:
                    if val.isdigit():
                        if len(val) > 1:
                            rege = rege + '\s+(?P<' + str('blank') + str(blankspace) + '>\d.+)'
                            blankspace = blankspace + 1
                        else:
                            rege = rege + '\s+(?P<' + str('blank') + str(blankspace) + '>\d+)'
                            blankspace = blankspace + 1
                    else:
                        rege = rege + '\s+(?P<' + str('blank') + str(blankspace) + '>\w.+)'
                        blankspace = blankspace + 1
            
            rs = img.crop((sorted_list[s][0], sorted_list[s][1], sorted_list[s][2] + 5, sorted_list[s][3] + 5))
            
            OCR = pytesseract.image_to_string(rs)
            OCR = OCR.strip()
            if OCR.isdigit():
                rege = rege + '\s+(?P<' + str(sorted_list[s][4]) + '>\d+)'
            else:
                k = OCR.split('.')
                if len(k) != 1:
                    rege = rege + '\s+(?P<' + str(sorted_list[s][4]) + '>'
                    for i in range(len(k)):
                        if k[i].isdigit():
                            if len(k) - 2 >= i:
                                rege = rege + '\d+\.'
                            else:
                                rege = rege + '\d+)'
                                break
                else:
                    if rege:
                        rege = rege + '\s+(?P<' + str(sorted_list[s][4]) + '>'
                        rege = rege + '.+)'
                    else:
                        rege = rege + '\s*(?P<' + str(sorted_list[s][4]) + '>'
                        rege = rege + '.+)'
            if len(sorted_list) - 1 > s and sorted_list[s][5] < sorted_list[s + 1][7] and sorted_list[s][5] != sorted_list[s + 1][7] and sorted_list[s][6] < sorted_list[s + 1][8] and sorted_list[s][6] != sorted_list[s + 1][8]:
                Middelval = img.crop((sorted_list[s][5], sorted_list[s][6], sorted_list[s + 1][7] + 5, sorted_list[s + 1][8] + 5))
                Middelval = pytesseract.image_to_string(Middelval)
                Middelval = Middelval.strip()
                if Middelval:
                    if Middelval.isdigit():
                        rege = rege + '\s+(?P<' + str('blank') + str(blankspace) + '>\d.+)'
                        blankspace = blankspace + 1
                    else:
                        rege = rege + '\s+(?P<' + str('blank') + str(blankspace) + '>\w.+)'
                        blankspace = blankspace + 1
        returnvaluelist = []
        returnvaluelist.append(rege)
        returnvaluelist.append(startvalue)
        return rege
    
    def getHeaderLabel(self,OCR_Text,value):
        try:
            mention_regex = value
            matches = re.findall(f'(.+?)({mention_regex})', OCR_Text)

            for match in matches:
                headervalue = ""

                preceding_string = match[0].split()
                mention = match[1]
                for num, val in enumerate(preceding_string[::-1]):
                    if num == 3:
                        break
                    headervalue = val + " " + headervalue
                
                return headervalue
        except Exception as ex:
            logger.log(f"Exception raise while creating a header value for {mention_regex} : {ex}","0")