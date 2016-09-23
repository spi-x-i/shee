# shee
A simple dstat data visualization tool

## Peel configuration

Just add dstat to your systems configuration, i.e.:
```
@Bean(name = Array("flink-1.0.3"))
  def `flink-1.0.3`: Flink = new Flink(
    version      = "1.0.3",
    configKey    = "flink",
    lifespan     = Lifespan.EXPERIMENT,
    dependencies = Set(ctx.getBean("dstat-0.7.2", classOf[Dstat])),
    mc           = ctx.getBean(classOf[Mustache.Compiler])
  )
```

## Requirements

We require numpy >= 1.11, matplotlib >= 1.3.1, pandas >= 0.18. So either install these:
```
sudo pip install numpy
sudo pip install matplotlib
sudo pip install pandas
```
or upgrade them:
```
sudo pip install --upgrade numpy
sudo pip install --upgrade matplotlib
sudo pip install --upgrade pandas
```



## Setup

```
git clone https://github.com/spi-x-i/shee.git
sudo python setup.py develop
```

## Let's do some charts
Peel will save the dstats results in the following way:
```
../peel_bundle/results/suite/experiment.runXX/logs/dstat/dstat-0.7.2/
```
So let's jump there:
```
cd ../peel_bundle/results/suite/experiment.runXX/logs/dstat/dstat-0.7.2/
```
and create charts specific for every single node:
```
python -m shee
```
If you want to get charts aggregated for the whole cluster you can run:
```
python -m shee -O -a
```

