FROM php:7.4-apache

# Install MySQL extensions
RUN apt-get update && \
    apt-get install -y default-mysql-client && \
    docker-php-ext-install mysqli pdo pdo_mysql && \
    a2enmod rewrite && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /var/www/html
