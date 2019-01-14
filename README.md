# serve_titles

### serves Land Registry titles froma local .CSV file over REST Api

Python, docker, Flask, pandas, shelve

### docker
docker gives us control over a container in which to run the app, particularly pandas and the .csv file. Files can run to 3.5Gb and loading and querying can be CPU intensive. So the `cpus`, `mem_limit` & `memswap_limit` are set in `docker-compose.yml` to prevent the dev machine falling over.

### memory issues

This implemtation uses waaay more memory than it needs to. With `debug==True` in `run.py` it uses twice as much. There is also apparently a memory leak (TODO: investigate). So adding a healthy whack of swap memory can help. Something like:
```
sudo fallocate -l 12G ../swapfile
sudo mkswap ../swapfile
sudo swapon ../swapfile
```

#### Run via docker
Make sure docker is running with `sudo systemctl start docker`

`cd serve_titles`

`docker-compose up --build`

or just `docker-compose up`

(may require `sudo` depending on docker installation)


#### Wait for it to load
Yeah, yeah, I know it's 2019. But this is a prototype - pandas is not the fastest backend!

You should see > Done :)

You can also run `docker stats` and/ or `sudo swapon --show` to check progress. The memory used will increase to the maximum (6Gb), then level out and start swapping out back down to your swappiness level. Swappiness ==15 => 6MB*(100-15%)= 5.1Gb

#### Query it
at `http://localhost:5000/title/13323` (13323 is a valid title number)



### Learnings
#### JSON in Flask is a pain
because it's not JSON. Flask will happily serve up NaN or Infinity as valid JSON primitives. It's nice that Flask takes care of a lot, such as Content-Type, but the flip side is that its JSONENcoder is buried deep and it's quicker to override it with a compliant encoder (just load in the same encoder and set a flag (or use `simplejson`) and then wrap it in a class ) than it is to clean the data before it reeaches. There is also the problem of passing around `null` before JSON is encoded. `None` translates to `null` in `simplejson` so map `NaN`s to `None` and convert `numpy` types instead of using `pandas`' own conversion.

#### Class methods in Flask Resources behave oddly
weird async effects - `eval` is used somewhere inside `Flask` so syntax errors are not caught until runtime. Logging with `print` waits until the class method is done. And there are probably more surprises to discover here.
