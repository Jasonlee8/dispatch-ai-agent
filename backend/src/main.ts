import 'dotenv/config';

import type { INestApplication } from '@nestjs/common';
import { ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import * as bodyParser from 'body-parser';
import cookieParser from 'cookie-parser';
import * as express from 'express';
import morgan from 'morgan';

import { GlobalExceptionFilter } from '@/common/filters/global-exception.filter';
import { setupSwagger } from '@/config/swagger.config';
import { winstonLogger } from '@/logger/winston.logger';
import { AppModule } from '@/modules/app.module';
async function bootstrap(): Promise<void> {
  console.log("===== NEST STARTING =====");
  console.log("MONGO_URI =", process.env.MONGO_URI);
  console.log("MONGO_DB =", process.env.MONGODB_URI);

  const app: INestApplication = await NestFactory.create(AppModule);
  app.useLogger(winstonLogger);
  app.use('/api/webhooks/stripe', express.raw({ type: 'application/json' }));
  app.setGlobalPrefix('api');
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      forbidUnknownValues: true,
    }),
  );
  // app.enableCors({
  //   origin: process.env.CORS_ORIGIN ?? '*',
  //   credentials: true, // Enable cookies in CORS
  // });
  app.enableCors({
    origin: process.env.APP_URL ?? '*',   // ★ 不能再用 '*' 了
    credentials: true,                 // 允许携带 cookie
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    allowedHeaders: [
      'Content-Type',
      'x-csrf-token',
      'Authorization',
    ],
  });


  app.use(cookieParser()); // Add cookie parser middleware
  app.useGlobalFilters(new GlobalExceptionFilter());
  app.use(morgan('combined'));
  app.use(bodyParser.urlencoded({ extended: false }));
  setupSwagger(app);

  const port = process.env.PORT ?? 4000;
  await app.listen(port);

  const adelaideTime = new Date().toLocaleString('en-AU', {
    timeZone: 'Australia/Adelaide',
  });
  winstonLogger.log('info', `App running at ${adelaideTime}`);
}

void bootstrap();
