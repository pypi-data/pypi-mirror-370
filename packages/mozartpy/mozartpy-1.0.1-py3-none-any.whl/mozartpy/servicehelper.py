import zeep  # soap 통신에 사용되는 package
import requests
import json
import tqdm
import os
import zipfile
import py7zr
from datetime import datetime
from multipledispatch import dispatch

class Downloader:
    """
    Baseclass for Mozart zip file download from the server using Mozart OutFileService

    :param url: Mozart server url with port number
    :param subDir: File location to download from the Mozart server
    :param wcf : True - Ver1 mozart outfileservice, False - Ver2 rest api service
    :example : ml = Downloader('http://192.168.1.2:8000/mozart/OutFileService','VDDF_RTS', False)

    Methods defined here:
    -- GetFileList() : Return file name list from the server subDir
    -- DownloadFiles(file_list, destination, unzipSwitch=True) : Download Mozart model files for the given file_list to save downloadPath
    -- DownloadFiles(fromDate, toDate, destination, unzipSwitch=True) :Download Mozart model files for the given date period to save downloadPath
    -- DownloadFiles(count, destination, unzipSwitch = True) : Download Mozart model files based on the given number of recently created models

    """
    def __init__(self, url, subDir, wcf):
        self.url = url
        self.subDir = subDir
        self.wcf = wcf

        if wcf:
            self.url = '{0}/mex?wsdl'.format(url)
            self.client = None

            try:
                self.client = zeep.Client(wsdl=self.url)
            except ConnectionError as error:
                raise Exception('Connection failed. Wrong or inaccessible hostname:'.format(error=error))
        else:
            self.headers = {'Content-Type': 'application/json', 'charset': 'UTF-8', 'Accept': '*/*'}
            self.method = 'POST'

    def GetFileList(self):
        """
        Return file name list from the server subDir

        :return: model file list(list<string>)
        """
        if self.wcf:
            files = self.client.service.GetFileList2(self.subDir)
        else:
            body = {"path": "Auto", "dir": self.subDir}
            s = requests.Session()
            target_url = '{0}/api/ofs/getFileList'.format(self.url)
            try:
                with s.post(target_url, headers=self.headers, data=json.dumps(body).encode('utf-8'), stream=True) as r:
                    # r.raise_for_status()
                    files = r.json().get('files')

                    # print("response status %r" % r.status_code)
                    # print("response text %r" % response.text)
            except Exception as ex:
                print(ex)
            s.close()

        return files

    def __checkDir__(self, destination):
        filedir = destination
        if not os.path.exists(filedir):
            print('{0} is not exist path :'.format(filedir))
            pass

    def __downloadFromV1Service__(self, file_list, destination, unzipSwitch):
        downloadedFiles = []
        for fname in file_list:
            filesize = self.client.service.GetFileSize2(fname, self.subDir)

            offset = 0
            chunkSize = 0x10000  # 10Mbytes
            count = filesize

            progress = tqdm.tqdm(range(filesize), f"Receiving {fname}", unit="B", unit_scale=True,ascii=True,
                                 unit_divisor=1024)
            # progress = tqdm.tqdm(range(filesize), f"Receiving {fname}", ascii=True)

            filePath = os.path.join(destination, fname)
            with open(filePath, 'wb') as f:
                f.seek(offset, 0)
                while offset < filesize:
                    if filesize >= chunkSize:
                        count = chunkSize
                    buffer = self.client.service.GetFileChunk2(fname, self.subDir, offset, count)
                    if not buffer:
                        break

                    f.write(buffer)
                    offset += len(buffer)
                    progress.update(len(buffer))

                downloadedFiles.append(filePath)
            if unzipSwitch:
                self.__unzip__(fname, destination)

            progress.close()
        # delete zipfile
        if unzipSwitch:
            for dfile in downloadedFiles:
                os.remove(dfile)

    def __downloadFromV2Service__(self, file_list, destination, unzipSwitch):
        targeturl = '{0}/api/ofs/getFile'.format(self.url)
        downloadedFiles = []
        for fname in file_list:
            body = {"path": "Auto", "subDir": self.subDir, "fileName": fname}
            filepath = os.path.join(destination, fname)
            tqdm_dict = {}
            s = requests.Session()
            try:
                if self.method == 'GET':
                    response = requests.get(self.url, headers=self.headers)
                elif self.method == 'POST':
                    # response = requests.post(url, headers=headers, data=json.dumps(body).encode('utf-8'))
                    with s.post(targeturl, headers=self.headers, data=json.dumps(body).encode('utf-8'), stream=True) as r:
                        # r.raise_for_status()
                        with open(filepath, 'wb') as f:
                            # 파일 크기 가져오기
                            file_size = int(r.headers.get('Content-Length', 0))
                            # tqdm 객체 생성
                            tqdm_dict[fname] = tqdm.tqdm(range(file_size), f"Receiving {fname}", unit="B",
                                                            unit_scale=True, ascii=True, leave=True,
                                                            unit_divisor=1024)
                            # 파일 다운로드
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                                tqdm_dict[fname].update(len(chunk))

                    downloadedFiles.append(filepath)
                    # tqdm 객체 삭제
                    del tqdm_dict[fname]

                    # print("response status %r" % r.status_code)
                    # print("response text %r" % response.text)
            except Exception as ex:
                print(ex)
            s.close()

            if unzipSwitch:
                self.__unzip__(fname, destination)

        # delete zipfile
        if unzipSwitch:
            for dfile in downloadedFiles:
                os.remove(dfile)

    def __unzip__(self, filename, destination ):
        splitFileNames = os.path.splitext(filename)
        if splitFileNames.__len__() < 2:
            pass

        filepath = os.path.join(destination, filename)
        zipdir = splitFileNames[0]
        try:
            if zipfile.is_zipfile(filepath):
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(destination, zipdir))
                    # mainProgress.set_description(f'{filename} unzip complete')
                # print(f'{filename} unzip complete')
            elif splitFileNames[1] == '.7z':
                # 7z 파일 압축 해제
                with py7zr.SevenZipFile(filepath, mode='r') as z:
                    z.extractall(path=os.path.join(destination, zipdir))
                    # mainProgress.set_description(f'{filename} unzip complete')
            else:
                pass
        except ConnectionError as error:
            print(filepath)
            print(zipdir)
            raise error

    @dispatch(list, str, bool)  # for function overloading
    def DownloadFiles(self, file_list, destination, unzipSwitch=True):
        """
        Download Mozart model files for the given file_list to save downloadPath

        :param file_list: model file list to download(list<string>)
        :param destination: local file path to save the downloaded files
        :param unzipSwitch: if true, the zip file is unzipped after downloading
        :return:

        """
        if not os.path.exists(destination):
            raise Exception('{0} is not exist path :'.format(destination))

        if self.wcf:
            self.__downloadFromV1Service__(file_list, destination, unzipSwitch)
        else:
            self.__downloadFromV2Service__(file_list, destination, unzipSwitch)
    @dispatch(list, str, unzipSwitch=None)  # for function overloading
    def DownloadFiles(self, file_list, destination, unzipSwitch=True):
        """
        Download Mozart model files for the given file_list to save downloadPath

        :param file_list: model file list to download(list<string>)
        :param destination: local file path to save the downloaded files
        :param unzipSwitch: if true, the zip file is unzipped after downloading
        :return:

        """
        if not os.path.exists(destination):
            raise Exception('{0} is not exist path :'.format(destination))

        if self.wcf:
            self.__downloadFromV1Service__(file_list, destination, unzipSwitch)
        else:
            self.__downloadFromV2Service__(file_list, destination, unzipSwitch)

    @dispatch(datetime, datetime, str, bool)#for function overloading
    def DownloadFiles(self, fromDate, toDate, destination, unzipSwitch=True):
        """
        Download Mozart model files for the given date period to save downloadPath

        :param fromDate: Start Date(datetime)
        :param toDate: End Date(datetime)
        :param destination: local file path to save the downloaded files
        :param unzipSwitch: if true, the zip file is unzipped after downloading
        :return:
        """
        filedir = destination
        if not os.path.exists(filedir):
            raise Exception('{0} is not exist path :'.format(filedir))

        files = self.GetFileList()
        if files == None:
            print('There is no data')
            pass

        downloadFiles = []
        for fname in files:
            tmp = os.path.splitext(fname)
            if tmp.__len__() < 2:
                continue

            dateStr = tmp[0][-14:]
            try:
                runTime = datetime.strptime(dateStr, '%Y%m%d%H%M%S')
            except:
                print('{0} cannot recognize date :'.format(fname))
                continue

            if fromDate > runTime or runTime > toDate:
                continue

            downloadFiles.append(fname)
        if downloadFiles.__len__() == 0:
            print('There is no data to download : {0} ~ {1}'.format(fromDate, toDate))
            pass

        self.DownloadFiles(downloadFiles, destination, unzipSwitch)

    @dispatch(datetime, datetime, str, unzipSwitch=None)  # for function overloading
    def DownloadFiles(self, fromDate, toDate, destination, unzipSwitch=True):
        """
        Download Mozart model files for the given date period to save downloadPath

        :param fromDate: Start Date(datetime)
        :param toDate: End Date(datetime)
        :param destination: local file path to save the downloaded files
        :param unzipSwitch: if true, the zip file is unzipped after downloading
        :return:
        """
        filedir = destination
        if not os.path.exists(filedir):
            raise Exception('{0} is not exist path :'.format(filedir))

        files = self.GetFileList()
        if files == None:
            print('There is no data')
            pass

        downloadFiles = []
        for fname in files:
            tmp = os.path.splitext(fname)
            if tmp.__len__() < 2:
                continue

            dateStr = tmp[0][-14:]
            try:
                runTime = datetime.strptime(dateStr, '%Y%m%d%H%M%S')
            except:
                print('{0} cannot recognize date :'.format(fname))
                continue

            if fromDate > runTime or runTime > toDate:
                continue

            downloadFiles.append(fname)
        if downloadFiles.__len__() == 0:
            print('There is no data to download : {0} ~ {1}'.format(fromDate, toDate))
            pass

        self.DownloadFiles(downloadFiles, destination, unzipSwitch)

    @dispatch(int, str, unzipSwitch=None)
    def DownloadFiles(self, count, destination, unzipSwitch = True):
        """
        Download Mozart model files based on the given number of recently created models

        :param count: Number of models to download
        :param destination: local file path to save the downloaded files
        :param unzipSwitch: if true, the zip file is unzipped after downloading
        :return:
        """

        self.__checkDir__(destination)

        files = self.GetFileList()

        downloadFiles = []
        chkCnt = 0
        for fname in files:
            if chkCnt == count:
                break
            downloadFiles.append(fname)
            chkCnt += 1

        self.DownloadFiles(downloadFiles, destination, unzipSwitch)

    @dispatch(int, str, bool)
    def DownloadFiles(self, count, destination, unzipSwitch=True):
        """
        Download Mozart model files based on the given number of recently created models

        :param count: Number of models to download
        :param destination: local file path to save the downloaded files
        :param unzipSwitch: if true, the zip file is unzipped after downloading
        :return:
        """

        self.__checkDir__(destination)

        files = self.GetFileList()

        downloadFiles = []
        chkCnt = 0
        for fname in files:
            if chkCnt == count:
                break
            downloadFiles.append(fname)
            chkCnt += 1

        self.DownloadFiles(downloadFiles, destination, unzipSwitch)