# MS-Renew

这是一个基于AutoApiS项目的一个分支。  
由于源仓库已经被删除，因此本仓库使用[OFFICE_E5_AUTO_API](https://github.com/ytmpscy/OFFICE_E5_AUTO_API)仓库中的源码进行修改。  
本项目较源项目添加Token加密，同时优化了Action脚本策略。 

## 注意
本项目仅适合有python和git基础的朋友尝试。  

## 使用方法
1. Fork本项目并Clone到本地  
   由于本项目添加了加密，因此不同于源项目，您需要先将项目克隆到本地进行修改。  

2. 获取所需的信息  
   本项目需要微软的应用ID，机密与refresh_token运行。  
   应用ID与机密获取方法参考官方文档：https://learn.microsoft.com/zh-cn/rest/api/datacatalog/register-a-client-app  
   refresh_token请使用rclone等工具获取，教程随便搜一下就有了，关键字：使用rclone获取refresh_token。  
   另，找到一个原版的教程，可以参考（如果挂了我就没辙了）：https://www.ioiox.com/archives/103.html  

3. 将获取的token保存  
   在token文件夹下，有0.txt文件。你需要将你上一步获取到的refresh_token复制粘贴到这个文件中。  
   如果你有n个账户需要调用，则按顺序依次按照0.txt 1.txt ... n.txt创建文件并保存token即可。  

4. 生成加密的token  
   本项目refresh_token使用AES算法进行加密，因此需要先将自己的refresh_token进行一次加密。  
   首先，确保自己电脑上有python3环境。  
   然后，需要安装两个依赖：  
   ```shell
    pip install requests pycryptodome
   ```  
   最后，运行加密脚本。  
   注意，下面的```$PASSWORD```替换成你自己想设置的任意密码。  
   ```$ID_LIST```替换成应用ID列表，如果有多个ID用空格隔开，如果只有一个则只写一个即可。（必须和第三步中的顺序一致）  
   ```$KEY_LIST```替换成应用ID列表，如果有多个ID用空格隔开，如果只有一个则只写一个即可。（必须和第三步中的顺序一致）  
   ```shell
    python GetEncryptToken.py $PASSWORD $ID_LIST $KEY_LIST

    # 样例
    python GetEncryptToken.py password id_1 id_2 id_3 key_1 key_2 key_3
   ```  

5. 推送  
   最后，你需要将修改后的内容push回自己的github。  
      ```shell
    git add .
    git commit -m "Commit Message"
    git push
   ```  

6. 添加Action参数
   在GitHub网页中，找到项目的Setting > Secrets > Add a new secret，新建三个secret：ID_LIST、KEY_LIST、PASSWORD 。  
   注意，这里的这三个secret应与上面运行脚本时的一致。 

    ID_LIST
    ```shell
    账号0应用id 账号n应用id
    ```
    
    KEY_LIST  
    ```shell
    账号0应用机密 账号n应用机密
    ```
    
    PASSWORD
    ```shell
    自己随便设置一个密码即可
    ```

7. GITHUB_TOKEN  
   进入你的个人设置页面(右上角头像 Settings，不是仓库里的 Settings)，选择 Developer settings > Personal access tokens > Generate new token，设置名字为GITHUB_TOKEN , 然后勾选 repo , admin:repo_hook , workflow 等选项，最后点击Generate token即可。

8. 可选：参数修改（以下内容来自源项目）  
   找到TestApi.py，按照以下提示进行参数修改，修改后不要忘记提交到仓库并推送：  
   ```shell
      * 每次轮数：每启动一次运行多少轮api调用，一轮调用10个api

      * 是否启动随机时间：每一轮结束隔“多久”才开始下一轮调用，这个“多久”会根据后面的参数随机生成

      * 延时范围起始，结束：例如设置600跟1200，则“多久”会在600到1200秒这个范围随机生成一个数，到时间开启下一轮调用

      * 是否开启随机api顺序:随机排序10个api，我设置的是15天换一次顺序，这个“15天”在.github/workflow/randapi.yml的schedule的cron里设置
      
      * 是否开启各api延时：就是每个api调用要不要停一下才开始下一个api调用。（个人建议不开）
        同样有范围，例如：分延时范围开始跟分结束分别设置为10，20.则会在10到20秒这个范围随机生成一个数，然后调用下一个api

      （由于延时需要长时间运行，测试的时候建议把随机、延时都关了，迅速运行完看看看情况，再更改喜欢的配置）
   ```  

9. 验证可用性  
    本项目Action已监听star动作，所以建议部署完毕后，自己给自己点一下项目星星，然后去Action栏中看一下是否正常执行了。

10. Action定时任务  
    这个会的人自己改就行，不会的人也没有改的必要，反正目前默认是每天执行三次，周日不执行。
