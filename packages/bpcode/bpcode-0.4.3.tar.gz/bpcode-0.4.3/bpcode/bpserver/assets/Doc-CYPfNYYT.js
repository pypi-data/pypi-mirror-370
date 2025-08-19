import{_ as a}from"./_plugin-vue_export-helper-DlAUqK2U.js";import{c as b,B as t,o as d}from"./index-z8FtxWqV.js";const o={},e={class:"doc"};function l(r,c){return d(),b("div",e,c[0]||(c[0]=[t(`<h2 data-v-8c8bcb38>bpcode 工具使用说明</h2><ol data-v-8c8bcb38><li data-v-8c8bcb38><strong data-v-8c8bcb38>服务端配置（必须先配置）</strong><ul data-v-8c8bcb38><li data-v-8c8bcb38> 在服务器用户目录下新建 <code data-v-8c8bcb38>.env</code> 文件，内容示例： <pre data-v-8c8bcb38>    BPCODE=你的密码
    BPATH=你的代码备份路径
                    </pre><p data-v-8c8bcb38><strong data-v-8c8bcb38>BPCODE</strong>：设置密码，只是为了防止误上传到他人服务器，现在反正也没什么人用，以后再说叭<br data-v-8c8bcb38><strong data-v-8c8bcb38>BPATH</strong>：必填，指定代码备份存储路径。 </p></li><li data-v-8c8bcb38> 安装 bpcode 并启动服务端： <pre data-v-8c8bcb38>pip install bpcode</pre><pre data-v-8c8bcb38>bpserver</pre><pre data-v-8c8bcb38>ufw allow 8888(ubuntu)总之自己开防火墙端口就行</pre></li></ul></li><li data-v-8c8bcb38><strong data-v-8c8bcb38>客户端使用</strong><ul data-v-8c8bcb38><li data-v-8c8bcb38> 在你的代码中添加如下内容（以 Python 为例）： <pre data-v-8c8bcb38>                from bpcode import backup
                a = backup.AutoBackUp(&quot;你的密码&quot;, &quot;http://服务器IP&quot;)
                        </pre></li><li data-v-8c8bcb38><pre data-v-8c8bcb38>                如何下载？
                安装完成后在终端输入 
                <code data-v-8c8bcb38>
                    bpdown --name 项目名称 --version 版本 --password 密码 --host 服务器IP
                </code>
                        </pre></li><li data-v-8c8bcb38><pre data-v-8c8bcb38>                    0.4.0 以后新增nas，可以在树莓派，玩客云等设备上使用，备份服务器代码
                    只需要在树莓派输入
                    bpnas
                    即可自动备份，打开http://服务器IP:8888/登录即可查看nas状态
                </pre></li><li data-v-8c8bcb38> 支持自动备份 <code data-v-8c8bcb38>.py</code>、<code data-v-8c8bcb38>.pyc</code>、<code data-v-8c8bcb38>.pt</code>、<code data-v-8c8bcb38>.pth</code> 等文件，修改后服务器自动同步版本。 </li><li data-v-8c8bcb38> 如有需要，可回退代码版本，类似于简易版的 git。 </li></ul></li><li data-v-8c8bcb38><strong data-v-8c8bcb38>工具作用</strong><ul data-v-8c8bcb38><li data-v-8c8bcb38> 解决深度学习开发中代码频繁拷贝、同步不及时、易丢失的问题。 </li><li data-v-8c8bcb38> 只需配置一次服务器，后续代码自动备份，无需手动操作。 </li></ul></li><li data-v-8c8bcb38><strong data-v-8c8bcb38>注意事项</strong><ul data-v-8c8bcb38><li data-v-8c8bcb38> 本工具安全性有限，不建议用于敏感项目。 接单，商务合作请联系微信：15035624220 </li></ul></li></ol>`,2)]))}const p=a(o,[["render",l],["__scopeId","data-v-8c8bcb38"]]);export{p as default};
