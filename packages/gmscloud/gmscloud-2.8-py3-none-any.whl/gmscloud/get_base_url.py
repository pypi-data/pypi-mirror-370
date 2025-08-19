def get_base_url(company_code):
    if company_code.lower() == "golden":
        return "https://client-api-golden.gmscloud.id"
    elif company_code.lower() == "stargas":
        return "https://client-api-stargas.gmscloud.id"
    elif company_code.lower() == "bgs":
        return "https://client-api-bgs.gmscloud.id"
    elif company_code.lower() == "sga":
        return "https://client-api-sga.gmscloud.id"
    elif company_code.lower() == "mbg":
        return "https://client-api-mbg.gmscloud.id"
    elif company_code.lower() == "demo":
        return "https://client-api-demo.gmscloud.id"
    elif company_code.lower() == "localhost":
        return "http://localhost:8001"
    return "https://localhost:8001"  
