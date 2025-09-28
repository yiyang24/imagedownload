# 用python下载北京故宫数字文物库原大图片

台北故宫大部分文物图片都开放下载了，北京故宫还不能下载，本人研究了以下方法下载北京故宫数字文物库的原大图片：
	
1. 打开北京故宫数字文物库https://digicol.dpm.org.cn/

2. 打开谷歌浏览器chrome的开发者工具devtools，点击想下载的图片进入全屏模式

3. 在源代码部分找到shuziwenku开头的文件夹下的relic文件夹下的最后一个文件夹

4. 点击图片放至最大，上下左右拖动图片，遍历图片的每个部分，该文件夹下会出现一个名为12的文件夹，打开后有0_0.jpg, 0_1.jpg等整张图片被分割成的“瓦片”（p1）
https://github.com/yiyang24/imagedownload/blob/8d03e4bb88c44cec97463324a5c0fd1ed3ab8151/20250927083211_240_59.png
5. 右键0_0.jpg，复制链接地址，粘贴至python代码（p2）中的base_url部分
https://github.com/yiyang24/imagedownload/blob/8d03e4bb88c44cec97463324a5c0fd1ed3ab8151/20250927082216_238_59.png
6. matrix_size为瓦片矩阵的大小，即整张图片被分成了几乘几的瓦片矩阵，如果12文件夹下的最后一张图片是1_3.jpg，那么就是1+1=2列，3+1=4行的矩阵，在matrix_size填入(4, 2)

7. 运行程序，程序会拼接所有瓦片（p3），程序运行完成后，检查生成在同目录下的stitched_image，如果图片不完整，就把matrix_size的行数或列数改大一点，重新运行程序
https://github.com/yiyang24/imagedownload/blob/8d03e4bb88c44cec97463324a5c0fd1ed3ab8151/20250927082241_239_59.png
8. 完成✅
