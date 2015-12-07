#encoding=utf-8
#功能：爬取淘宝上MM的信息
import urllib2
import urllib
import re
import os
#定义一个工具类来处理内容中的标签
class Tool:
	#去除img标签，7位长空格
	removeImg=re.compile('<img.*?>| {7}|')
	#去除超链接标签
	removeAddr=re.compile('<a.*?>|</a>')
	#把换行的标签换为\n
	replaceLine=re.compile('<tr>|<div>|</div>|</p>')
	#将表格制表<td>替换为\t
	replaceTD=re.compile('<td>')
	#把段落开头换为\n加空两格
	replacePara=re.compile('<p.*?>')
	#将换行符或双换行符替换为\n
	replaceBR=re.compile('<br><br>|<br>')
	#将其余标签删除
	removeExtraTag=re.compile('<.*?>')
	def replace(self,x):
		x=re.sub(self.removeImg,"",x)
		x=re.sub(self.removeAddr,"",x)
		x=re.sub(self.replaceLine,"\n",x)
		x=re.sub(self.replaceTD,"\t",x)
		x=re.sub(self.replacePara,"\n  ",x)
		x=re.sub(self.replaceBR,"\n",x)
		x=re.sub(self.removeExtraTag,"",x)
		return x.strip()
#访问地址:URL="https://mm.taobao.com/json/request_top_list.htm?page=1"
class TaoBao:
	def __init__(self,baseUrl,page):
		self.tool=Tool()
		self.baseUrl=baseUrl
		self.page=page
		self.url=self.baseUrl+"?page="+self.page
		self.content=None#加入一个content属性
	def getPageHtml(self):
		user_agent="Mozilla/5.0 (Windows NT 6.1)"
		headers={"User-Agent":user_agent}
		try:
			request=urllib2.Request(self.url,headers=headers)
			response=urllib2.urlopen(request)
			content=response.read()
			self.content=content
			#print content #测试输出
			#return content
		except urllib2.URLError,e:
			if hasattr(e,"reason"):
				print u"连接出错"+e.reason
	#得到名字
	def getName(self):
		pattern=re.compile(r'<a class="lady-name.*?>(.*?)</a>',re.S)
		items=re.findall(pattern,self.content)
		for item in items:
			print item
	#得到年纪
	def getAge(self):
		pattern=re.compile(r'<a class="lady-name.*?<strong>(.*?)</strong>',re.S)
		items=re.findall(pattern,self.content)
		for item in items:
			print item
	#上面是单一的获取MM的名字和年纪，下面写一个函数对MM的名字、年纪、哪里人一起获取
	def getMMInformation(self):
		pattern=re.compile(r'<div class="list-item".*?<a href="(.*?)".*?<img src="(.*?)".*?<a class="lady-name".*?>(.*?)</a>.*?<strong>(.*?)</strong>.*?<span>(.*?)</span>',re.S)
		items=re.findall(pattern,self.content)
		#下面为测试输出
		for item in items:
			print item[0],item[1],item[2],item[3],item[4]
		#将上面这些信息保存到文件中
		contents=[]
		for item in items:
			contents.append([item[0],item[1],item[2],item[3],item[4]])
		return contents
		
	
	#将获取的信息保存到文件
	#1、将获取的图片信息保存到目录中
	def saveImg(self,imgLink,fileName):
		img=urllib2.urlopen(imgLink)
		imgContent=img.read()
		f=open(fileName,'wb')
		f.write(imgContent)
		f.close()
	#功能：保存个人简介
	def saveBrief(self,data,fileName):
		fileName=fileName+"/"+fileName+"information.txt"
		f=open(fileName,"wb+")
		print u"正在保存信息到文件中"
		f.write(data.encode("utf-8"))
		f.close()
	#创建一个即将要存储信息的目录
	def mkdir(self,path):
		path=path.strip()
		#先判断这个路径是否存在
		isExist=os.path.exists(path)#如果存在，则为True
		if not isExist:
			os.makedir(path)
			return True
		else:
			print u"该目录已经存在"
			return False
	#根据MM的个人信息的URL，来获取该页面上该MM的个人简介和所有的图片
	def getDetailPage(self,url):
		htmlContent=urllib2.urlopen(url)
		return htmlContent.read()
	#从页面的html代码中得到MM的个人简介
	def getBrief(self,content):
		pattern=re.compile('<div class="mm-aixiu-content".*?>(.*?)<!--',re.S)
		result=re.search(pattern,content)
		return self.tool.replace(result.group(1))
	#获取MM网页上的所有图片
	def getAllImg(self,content):
		pattern=re.compile(r'<img style=".*?src="(.*?)">.*?</strong>',re.S)
		images=re.findall(pattern ,content)
		return images
	#参数为：很多的图片地址,和MM的名字
	def saveImgs(self,images,name):
		number = 1
		print u"发现",name,u"共有",len(images),u"张照片"
		for imageURL in images:
			splitPath = imageURL.split('.')
			fTail = splitPath.pop()
			if len(fTail) > 3:
				fTail = "jpg"
			fileName = name + "/" + str(number) + "." + fTail
			self.saveImg(imageURL,fileName)
			number += 1
	# 保存头像
	def saveIcon(self,iconURL,name):
		splitPath = iconURL.split('.')
		fTail = splitPath.pop()
		fileName = name + "/icon." + fTail
		self.saveImg(iconURL,fileName)
	def savePageInfomation(self):
		contents=self.getMMInformation()
		#item[0]为个人信息的URL,item[1]为MM图像URL,item[2]为MM名字,item[3]为MM年纪,item[4]为MM位置
		for item in contents:
			print u"发现了一位模特，名字、年龄和位置为：",item[2],item[3],item[4]
			print u"正在保存",item[2],u"的全部信息"
			#个人详情页面的URL
			detailURL=item[0]
			#得到个人详情页面的代码
			detailPageContent=self.getDetailPage(detailURL)
			#获取个人简介
			brief=self.getBrief(detailPageContent)
			#获取所有图片列表
			images=self.getAllImg(detailPageContent)
			self.mkdir(item[2])#根据MM的名字来创建目录
			#保存个人简介
			self.saveBrief(brief,item[2])
			#保存图像
			self.saveIcon(item[1],item[2])
			#保存图片
			self.saveImgs(images,item[2])
			

#url=raw_input("input a url:")
url="https://mm.taobao.com/json/request_top_list.htm"
page=raw_input("input a page:")
taobao=TaoBao(url,page)
taobao.getPageHtml()
# taobao.getName()
# taobao.getAge()
contents=taobao.getMMInformation()
taobao.savePageInfomation()