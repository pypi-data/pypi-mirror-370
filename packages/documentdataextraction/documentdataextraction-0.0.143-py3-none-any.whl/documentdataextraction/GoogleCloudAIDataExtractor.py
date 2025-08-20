from invoice2data import extract_data
import loggerutility as logger
# from .GoogleDocumentai import quickstart
from .GenerateExtractTemplate import GenerateExtractTemplate 

class GoogleCloudAIDataExtractor:

    def Data_Process(self,file_path : str,templates : str, input_reader_module : str,template_folder : str):

        logger.log(f"extracting data start::{file_path}","0")
        try:
            result = {}
            resultdata = extract_data(invoicefile=file_path,templates=templates,input_module=input_reader_module)
            result["EXTRACT_TEMPLATE_DATA"] = resultdata
            # Added by SwapnilB [12-07-22] [START] for filterng json of supplier bill 
            if 'customer_name' in result.keys():
                result['customer_name'] = result['customer_name'].split(':')[1].strip()
                
            if 'GST_number' in result.keys():
                if ':' in result['GST_number']:
                    result['GST_number'] = result['GST_number'].split(':')[1].strip()
                
            if 'Order_number' in result.keys():
                result['Order_number'] = result['Order_number'].split(':')[1].strip()
                
            if 'Bill_number' in result.keys():
                result['Bill_number'] = result['Bill_number'].split(' ')[1].strip()
                
            if 'Bill_date' in result.keys():
                result['Bill_date'] = result['Bill_date'].date()   

        except Exception as e:
            print(str(e))
            if str(e) == "'bool' object has no attribute 'keys'":
                logger.log(f"yml creation code :::  {e}","0")
                templatecreation = GenerateExtractTemplate()
                templatecreation.generateTemplate('document-ai-370906', 'us', '6c25a8b04ae751c3',file_path,'application/pdf',template_folder)
                # quickstart('document-ai-370906', 'us', '6c25a8b04ae751c3',file_path,'application/pdf',template_folder)
            else:
                logger.log(f"Issue:::  {e}","0")  
                
        return result