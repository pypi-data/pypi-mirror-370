FROM php:8.2-alpine

RUN apk add --no-cache git
RUN apk add --no-cache zlib-dev
RUN apk add --no-cache libpng-dev
RUN apk add --no-cache libzip-dev
RUN apk add --no-cache libxslt-dev
RUN apk add --no-cache icu-dev
RUN apk add --no-cache yarn
RUN apk add --no-cache $PHPIZE_DEPS
RUN apk add --no-cache linux-headers

RUN docker-php-ext-install gd
RUN docker-php-ext-install zip
RUN docker-php-ext-install pdo_mysql
RUN docker-php-ext-install exif
RUN docker-php-ext-install bcmath
RUN docker-php-ext-install xsl
RUN docker-php-ext-install intl

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer

WORKDIR /app
RUN git clone https://github.com/koel/koel.git --branch v7.10.4 --single-branch --depth 1 .
RUN cp .env.example .env
RUN composer install
RUN yarn install
RUN yarn build
RUN php artisan key:generate
RUN php artisan koel:migrate
RUN php artisan koel:seed
RUN php artisan koel:install

ENTRYPOINT [ "php", "-S", "0.0.0.0:80" ]
