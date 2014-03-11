Podgy - The Webserver Log Analyser
==================================

WARNING: this project is incomplete and probably not that useful to anybody!

Podgy is a tool and library for parsing web server logs.

It aims to produce reports on the following metrics:

  - Page impressions
  - Unique visitors
  - Visits
  - Pages per visit

It's primary purpose is to validate information provided by Google Analytics and to give
simple realtime data which can be used in your own analyses.

Also included are some analysis examples for running as syslog-ng modules that can
capture from a cluster of app servers, storing aggregate values in redis for use by
[dashi dashboard](https://github.com/eurogamer/dashi).

It's still in development, and right now doesn't do that much :)

Configuration
-------------

The main Podgy processor reads its configuration from .podge files.  Podge files are XML (sorry)
of the form:

{{{
<podge>
	<globals>
		...global configuration vars...
	</globals>

	<exclusions>
		...robots and stuff...
	</exclusions>

	...one or more report definitions of the form:
	<report label="Eurogamer">
		...things to track, etc...
	</report>

</podge>
}}}

Future: modular configuration with imports, etc

Running
-------

To read from stdin:

```
python process.py -
```

To read from a logfile:

```
python process.py access.log
```


Testing your config syntax
--------------------------

Just run:

```
python config.py <podge file>
```

