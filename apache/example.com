<VirtualHost *:8080>
	ServerAdmin test@example.com

	ServerName example.com
	ServerAlias www.example.com

	#DocumentRoot /var/www/html/example.com

	WSGIDaemonProcess example.com user=www-data group=www-data threads=500
	WSGIProcessGroup example.com
	WSGIScriptAlias / /var/www/django/example/apache/example.wsgi

	<Directory /var/www/django/example/apache>
		Order deny,allow
		Allow from all
	</Directory>

	# Possible values include: debug, info, notice, warn, error, crit,
	# alert, emerg.
	LogLevel warn
	ErrorLog /var/log/apache2/example.com.error.log
	CustomLog /var/log/apache2/example.com.access.log combined

</VirtualHost>
