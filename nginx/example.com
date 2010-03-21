# You may add here your
# server {
#	...
# }
# statements for each of your virtual hosts

upstream example_backend {
  server 127.0.0.1:8080;
}

server {
	listen 80;
	server_name www.example.com;
	rewrite ^/(.*) http://example.com/$1 permanent;
}

server {
	listen 80;
	server_name example.com;

	access_log  /var/log/nginx/example.com.access.log;
	error_log  /var/log/nginx/example.com.error.log;

	location / {
		proxy_pass http://example_backend;
		include /etc/nginx/proxy.conf;
	}

	location /media/ {
		root   /var/www/html/example.com;
		#index  index.html index.htm;
	}
}


# another virtual host using mix of IP-, name-, and port-based configuration
#
#server {
#listen   8000;
#listen   somename:8080;
#server_name  somename  alias  another.alias;

#location / {
#root   html;
#index  index.html index.htm;
#}
#}


# HTTPS server
#
#server {
#listen   443;
#server_name  localhost;

#ssl  on;
#ssl_certificate  cert.pem;
#ssl_certificate_key  cert.key;

#ssl_session_timeout  5m;

#ssl_protocols  SSLv2 SSLv3 TLSv1;
#ssl_ciphers  ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP;
#ssl_prefer_server_ciphers   on;

#location / {
#root   html;
#index  index.html index.htm;
#}
#}
