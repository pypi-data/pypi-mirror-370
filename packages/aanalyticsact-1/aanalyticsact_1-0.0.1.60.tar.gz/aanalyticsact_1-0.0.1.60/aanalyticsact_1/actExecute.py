# Created by Sunkyeong Lee
# Inquiry : sunkyeong.lee@concentrix.com / sunkyong9768@gmail.com
# Updated & Managed by Youngkwang Cho
# Inquiry : youngkwang.Cho@concentrix.com / ykc124@naver.com
# limit function and para order
# JsonToDB To refinedFrame1

from copy import Error
# from actModuler import *
# from actRunner import *
from .actModuler import *
from .actRunner import *
import time


def retrieve_FirstLevel(start_date, end_date, period, jsonLocation, tbColumn, dbTableName, epp, site_code_rs, limit=0, extra = "", extra1 = "", start_hour="00:00", end_hour="00:00", site_code = "", max_retries = 5):
    if limit > 10000:
        raise Error("limit은 0 ~ 10000 사이 값으로 넣어주세요")

    dateCaller = dateGenerator(start_date, end_date, period)
    if_site_code = checkSiteCode(readJson(jsonLocation)["dimension"])
    
    tbColumn = tbColumnGenerator(tbColumn, if_site_code, False, False, site_code_rs)
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    for i in range(len(startDate)):
        retry_count = 0
        while retry_count < max_retries:
            try:
                start = time.time()
                refinedFrame1(startDate[i], endDate[i], period, jsonLocation, tbColumn, dbTableName, epp, if_site_code, site_code_rs, limit, extra, extra1, start_hour, end_hour, site_code)
                break
            except EmptyDataError : 
            	print(startDate[i], endDate[i] )
            	break
            except KeyError:
                continue

            except IndexError:
                continue

            except AttributeError:
                continue

            except ConnectionError:
                continue

            except ConnectionResetError:
                continue 

            retry_count += 1
            if retry_count == max_retries:
                print(f"Max retries {max_retries} reached. Moving to the next task.")
            else:
                continue  
        timeSec = round(time.time() - start, 2)
        print("Time took: ", timeSec, "sec")

def retrieve_SecondLevel(start_date, end_date, period, jsonLocation, jsonLocation_breakdown,tbColumn, dbTableName, epp, limit1=0,limit2=0, extra = "", extra1 = "", start_hour="00:00", end_hour="00:00", site_code="", max_retries = 5):
    dateCaller = dateGenerator(start_date, end_date, period)
    if_site_code = checkSiteCode(readJson(jsonLocation)["dimension"])

    if returnRsID(jsonLocation) == "sssamsungnewus":
        if_site_code = True

    site_code_rs = False
    tbColumn = tbColumnGenerator(tbColumn, if_site_code, True, False, site_code_rs)
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    for i in range(len(startDate)):
        retry_count = 0
        while retry_count < max_retries:
            try:
                start = time.time()
                StackbreakValue(startDate[i], endDate[i], period, jsonLocation, jsonLocation_breakdown, tbColumn, dbTableName, epp, limit1, limit2, extra, extra1, start_hour, end_hour, site_code)
                break

            except KeyError:
                break
	
            except KeyError:
                continue

            except IndexError:
                continue

            except AttributeError:
                continue

            except ConnectionError:
                continue

            except ConnectionResetError:
                continue

            retry_count += 1
            if retry_count == max_retries:
                print(f"Max retries {max_retries} reached. Moving to the next task.")
            else:
                continue  

        timeSec = round(time.time() - start, 2)
        print("Time took: ", timeSec, "sec")
   
def retrieve_by_RS(start_date, end_date, period, jsonLocation, rsInput, tbColumn, dbTableName, epp, limit=0, extra = "", extra1 = "",start_hour="00:00", end_hour="00:00", max_retries = 5):
    dateCaller = dateGenerator(start_date, end_date, period)
    site_code_rs = False
    tbColumn = tbColumnGenerator(tbColumn, False, False, True, site_code_rs)
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    rsList = returnRsList(epp, rsInput)

    for j in range(len(rsList)):
        for i in range(len(startDate)):
            retry_count = 0
            while retry_count < max_retries:
                try:
                  start = time.time()
                  refineRsIDChange(startDate[i], endDate[i], jsonLocation, rsList[j], period, tbColumn, dbTableName, epp, limit, extra, extra1, start_hour, end_hour)
                  timeSec = round(time.time() - start, 2)
                  print("Time took: ", timeSec, "sec")
                  break

                except EmptyDataError:
                    print(rsList[j],startDate[i], endDate[i] )
                    break

                except KeyError:
                    print("Server Error occurred, please wait for the next response")
                    continue

                except IndexError:
                    print("Index Error occurred, please wait for the next response")
                    continue

                except AttributeError:
                    print("Connection Error occurred, please wait for the next response")
                    continue

                except ConnectionError:
                    print("Connection Error occurred, please wait for the next response")
                    continue

                except ConnectionResetError:
                    continue

            retry_count += 1
            if retry_count == max_retries:
                print(f"Max retries {max_retries} reached. Moving to the next task.")
            else:
                continue  
    


def retrieve_by_RS_breakdown(startDate, endDate, period, jsonFile, jsonFilebreakdown, rsInput, tbColumn, dbTableName, epp, limit1=0, limit2=0, extra = "", extra1 = "",start_hour = "00:00", end_hour = "00:00", max_retries = 5):
    dateCaller = dateGenerator(startDate, endDate, period)
    defaultColumn = ["site_code", "dimension", "breakdown", "period", "start_date", "end_date", "is_epp"]
    
    if extra != "":
        defaultColumn.append("extra")
    if extra1 != "":
        defaultColumn.append("extra1")

    newColumn = defaultColumn + tbColumn

    startDate = dateCaller[0]
    endDate = dateCaller[1]

    rsList = returnRsList(epp, rsInput)

    for j in range(len(rsList)):
        for i in range(len(startDate)):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    start = time.time()
                    secondCaller(startDate[i], endDate[i], jsonFile, jsonFilebreakdown, rsList[j],  period, newColumn, dbTableName, epp, limit1, limit2, extra, extra1, start_hour, end_hour)
                    break

                except EmptyDataError : 
                    print(rsList[j],startDate[i], endDate[i] )
                    break

                except KeyError:
                    continue

                except IndexError:
                    continue

                except AttributeError:
                    continue

                except ConnectionError:
                    continue

                except ConnectionResetError:
                    continue

                retry_count += 1
                if retry_count == max_retries:
                    print(f"Max retries {max_retries} reached. Moving to the next task.")
                else:
                    continue   

            timeSec = round(time.time() - start, 2)
            print("Time took: ", timeSec, "sec")

def retrieve_RB(start_date, end_date, jsonLocation, rsInput, tbColumn, dbTableName, epp, limit=0, Biz_type = "", Device_type = "", Division = "", Category = "", max_retries = 5):
    start_hour="00:00"
    end_hour="00:00"
    period = "daily"
    dateCaller = dateGenerator(start_date, end_date, period)
    site_code_rs = False
    tbColumn = tbColumnGeneratorRB(tbColumn, False, False, True, site_code_rs)
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    rsList = returnRsList(epp, rsInput)

    for j in range(len(rsList)):
        for i in range(len(startDate)):
            retry_count = 0
            while retry_count < max_retries:
                try:
                  start = time.time()
                  refineRsIDChangeRB(startDate[i], endDate[i], jsonLocation, rsList[j], period, tbColumn, dbTableName, epp, limit, Biz_type,Device_type,Division,Category,"",start_hour, end_hour)
                  break  
                except EmptyDataError : 
                    print(rsList[j],startDate[i], endDate[i] )
                    break
                except KeyError:
                    continue
                except IndexError:
                    continue
                except AttributeError:
                   continue
                except ConnectionError:
                   continue

                retry_count += 1
                if retry_count == max_retries:
                    print(f"Max retries {max_retries} reached. Moving to the next task.")
            else:
                continue  
            timeSec = round(time.time() - start, 2)
            print("Time took: ", timeSec, "sec")

       
def retrieve_RB_AE(start_date, end_date, jsonLocation, rsInput, tbColumn, dbTableName, epp, limit=0, Biz_type = "", Device_type = "", Division = "", Category = "", site_code_ae ="", max_retries = 5):
    start_hour="00:00"
    end_hour="00:00"
    period = "daily"
    dateCaller = dateGenerator(start_date, end_date, period)
    site_code_rs = False
    tbColumn = tbColumnGeneratorRB(tbColumn, False, False, True, site_code_rs)
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    rsList = returnRsList(epp, rsInput)

    for j in range(len(rsList)):
        for i in range(len(startDate)):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    start = time.time()
                    refineRsIDChangeRB(startDate[i], endDate[i], jsonLocation, rsList[j], period, tbColumn, dbTableName, epp, limit, Biz_type,Device_type,Division,Category,site_code_ae,start_hour, end_hour)
                    break  
                except EmptyDataError : 
                    print(rsList[j],startDate[i], endDate[i] )
                    break
                except KeyError:
                    continue
                except IndexError:
                    continue
                except AttributeError:
                    continue
                except ConnectionError:
                    continue

                retry_count += 1
                if retry_count == max_retries:
                    print(f"Max retries {max_retries} reached. Moving to the next task.")
            else:
                continue  
            timeSec = round(time.time() - start, 2)
            print("Time took: ", timeSec, "sec")   


################UPDATE
def retrieve_by_RS_breakdownTotal(startDate, endDate, period, jsonFile, jsonFilebreakdown, rsInput, tbColumn, dbTableName, epp, limit1=0, limit2=0, extra = "", extra1 = "", start_hour = "00:00", end_hour = "00:00", max_retries = 5):
    dateCaller = dateGenerator(startDate, endDate, period)
    defaultColumn = ["site_code", "dimension", "breakdown", "period", "start_date", "end_date", "is_epp"]
    
    if extra != "":
        defaultColumn.append("extra")
    if extra1 != "":
        defaultColumn.append("extra1")

    newColumn = defaultColumn + tbColumn

    startDate = dateCaller[0]
    endDate = dateCaller[1]

    rsList = returnRsList(epp, rsInput)

    for j in range(len(rsList)):
        for i in range(len(startDate)):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    start = time.time()
                    refineRsIDChangeTotal(startDate[i], endDate[i], jsonFile, rsList[j], period, newColumn, dbTableName, epp, limit1, extra, extra1, start_hour, end_hour)
                    secondCaller(startDate[i], endDate[i], jsonFile, jsonFilebreakdown, rsList[j],  period, newColumn, dbTableName, epp, limit1, limit2, extra, extra1, start_hour, end_hour)
                    break
                except EmptyDataError : 
                	print(rsList[j],startDate[i], endDate[i] )
                	break
                except KeyError:
                    continue

                except IndexError:
                    continue

                except AttributeError:
                    continue

                except ConnectionError:
                    continue

                except ConnectionResetError:
                    continue

                retry_count += 1
                if retry_count == max_retries:
                    print(f"Max retries {max_retries} reached. Moving to the next task.")
            else:
                continue   

            timeSec = round(time.time() - start, 2)
            print("Time took: ", timeSec, "sec")


def retrieve_SecondLevelTotal(start_date, end_date, period, jsonLocation, jsonLocation_breakdown,tbColumn, dbTableName, epp, limit1=0, limit2=0, extra = "", extra1 = "", start_hour="00:00", end_hour="00:00", site_code="", max_retries = 5):
    dateCaller = dateGenerator(start_date, end_date, period)
    if_site_code = checkSiteCode(readJson(jsonLocation)["dimension"])

    if returnRsID(jsonLocation) == "sssamsungnewus":
        if_site_code = True

    site_code_rs = False
    tbColumn = tbColumnGenerator(tbColumn, if_site_code, True, False, site_code_rs)
    
    startDate = dateCaller[0]
    endDate = dateCaller[1]

    for i in range(len(startDate)):
        retry_count = 0
        while retry_count < max_retries:
            try:
                start = time.time()
                refinedFrameTotal(startDate[i], endDate[i], period, jsonLocation, tbColumn, dbTableName, epp, if_site_code, site_code_rs, limit1, extra, extra1, start_hour, end_hour, site_code)
                StackbreakValue(startDate[i], endDate[i], period, jsonLocation, jsonLocation_breakdown, tbColumn, dbTableName, epp, limit1, limit2, extra, extra1, start_hour, end_hour, site_code)
                break
            except EmptyDataError : 
                print(rsList[j],startDate[i], endDate[i] )
                break
            except KeyError:
                continue

            except IndexError:
                continue

            except AttributeError:
                continue

            except ConnectionError:
                continue

            except ConnectionResetError:
                continue

            retry_count += 1
            if retry_count == max_retries:
                print(f"Max retries {max_retries} reached. Moving to the next task.")
        else:
            continue  

        timeSec = round(time.time() - start, 2)
        print("Time took: ", timeSec, "sec")
