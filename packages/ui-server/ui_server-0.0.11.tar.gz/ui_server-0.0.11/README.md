## UIServer

A UI server for [RLtools](https://rl.tools) environments. Check out e.g. [rl-tools/l2f](https://github.com/rl-tools/l2f)


```
pip install ui-server
```


Run the UIServer
```
ui-server
```
Navigate to [http://localhost:13337](http://localhost:13337)
This is run separately from the client code such that you can keep the browser open, without windows popping up and going away when re-running your code. Also the camera perspective is maintained across runs.

**Alternatively**: Run in Docker
```
docker run -it --rm -p 13337:13337 python bash -c "pip install ui-server && ui-server"
```