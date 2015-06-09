# teatray

chat bridge tool

current support

* slack
* hipchat
* skype

## install

```
$ git clone http://github.com/wataken44/teatray.git
$ cd teatray
$ cp config-sample.json config.json
$ <edit config.json>
$ python teatray.py
```

note:
config.json, which credidentials(e.g. api_token) will be written, is in .gitignore. 

api_tokenなど認証情報を書くconfig.jsonは.gitignoreに入ってる。

## memo
### teatray needs account for bot
Skype|Slack|Hipchat account which will be used to bridge must be new account.
DON'T use your account.

Skype|Slack|Hipchatのアカウントは新しいアカウントである必要がある。
自分のアカウントは使わない。

### to bridge skype
teatray uses Skype4Py, which have some requirements:

* Skype Client must be running on X window
* The room to be bridged must be created by /createmoderatedchat
    * '/get name' must return 'name=#foobar...', must not return 'name=19:foobar...' 

teatrayはSkype4Pyを利用していて、必要条件がいくつかある:

* Skype ClientがX window上で動作していること
* bridgeされる部屋が/createmoderatedchat上で動作していること
    * '/get name'は'name=#foobar...'を返すこと。'name=19:foobar...'を返さないこと。

## todo

* comment書きましょう
* SkypeAdapter, SlackAdapter, HipchatAdapterのロジック共通部分多いので基底クラス作りましょう
* 各Adapterでreadonly, writeonlyできるようにしたい
* 出力フォーマットを修正できるようにしたい
* 特にhttpのerror handlingが適当なのでもう少しなんとかする
* daemon化したい


