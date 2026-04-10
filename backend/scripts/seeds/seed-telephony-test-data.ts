import { connect, connection, model, Schema, Types } from 'mongoose';
import * as bcrypt from 'bcryptjs';
import { randomUUID } from 'crypto';

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/dispatchai';
const SALT_ROUNDS = 10;

// 定义接口
interface User {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  twilioPhoneNumber: string;
  fullPhoneNumber: string;
  receivedAdverts: boolean;
  status: string;
  statusReason?: string;
  position?: string;
  role: string;
  googleId?: string;
  avatar?: string;
  provider: string;
  tokenRefreshTime?: Date;
  createdAt: Date;
  updatedAt: Date;
}

interface Service {
  name: string;
  description: string;
  price: number;
  userId: string;
  isAvailable: boolean;
  createdAt: Date;
  updatedAt: Date;
}

interface Company {
  businessName: string;
  email: string;
  abn: string;
  number: string;
  address: {
    unitAptPOBox?: string;
    streetAddress: string;
    suburb: string;
    state: string;
    postcode: string;
  };
  user: Types.ObjectId;  // 改为 ObjectId 类型
  createdAt: Date;
  updatedAt: Date;
}

// 创建 Schema
const userSchema = new Schema({
  firstName: String,
  lastName: String,
  email: { type: String, required: true, unique: true },
  password: String,
  twilioPhoneNumber: String,
  fullPhoneNumber: String,
  receivedAdverts: { type: Boolean, default: true },
  status: { type: String, default: 'active' },
  statusReason: String,
  position: String,
  role: { type: String, default: 'user' },
  googleId: String,
  avatar: String,
  provider: { type: String, default: 'local' },
  tokenRefreshTime: { type: Date, default: Date.now }
}, { timestamps: true });

const serviceSchema = new Schema({
  name: { type: String, required: true },
  description: String,
  price: { type: Number, required: true },
  userId: { type: String, required: true },
  isAvailable: { type: Boolean, default: true }
}, { timestamps: true });

const companySchema = new Schema({
  businessName: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  abn: { type: String, required: true, unique: true },
  number: { type: String, required: true },
  address: {
    unitAptPOBox: { type: String },
    streetAddress: { type: String, required: true },
    suburb: { type: String, required: true },
    state: { type: String, required: true },
    postcode: { type: String, required: true }
  },
  user: { type: Schema.Types.ObjectId, ref: 'User', required: true }
}, { timestamps: true });

async function seedTelephonyTestData() {
  try {
    await connect(MONGODB_URI);
    console.log('✅ Connected to MongoDB');
    
    // 创建 models
    const UserModel = model('User', userSchema);
    const ServiceModel = model('Service', serviceSchema);
    const CompanyModel = model('Company', companySchema);
    
    // 检查是否已存在测试用户
    const existingUser = await UserModel.findOne({ email: 'john.doe@example.com' });
    
    if (existingUser) {
      console.log('👤 Test user already exists, updating...');
      
      // 更新用户信息
      const hashedPassword = await bcrypt.hash('Admin123!', SALT_ROUNDS);
      await UserModel.updateOne(
        { email: 'john.doe@example.com' },
        {
          firstName: 'John',
          lastName: 'Doe',
          password: hashedPassword,
          // twilioPhoneNumber: '+19787235265',
          // fullPhoneNumber: '+19787235265',
          twilioPhoneNumber: '+61361601806',
          fullPhoneNumber: '+61400000000',
          receivedAdverts: true,
          status: 'active',
          statusReason: '',
          position: 'Business Owner',
          role: 'user',
          googleId: null,
          avatar: null,
          provider: 'local',
          tokenRefreshTime: new Date()
        }
      );
      
      // 删除该用户的现有服务和公司数据
      await ServiceModel.deleteMany({ userId: existingUser._id.toString() });
      await CompanyModel.deleteMany({ user: existingUser._id });  // 使用 ObjectId
      console.log('🧹 Cleared existing services and company data for test user');
      
      const testUser = existingUser;
      console.log('👤 Updated test user:', testUser.email);
    } else {
      console.log('👤 Creating new test user...');
      
      // 创建测试用户
      const hashedPassword = await bcrypt.hash('Admin123!', SALT_ROUNDS);
      const testUser = await UserModel.create({
        firstName: 'John',
        lastName: 'Doe',
        email: 'john.doe@example.com',
        password: hashedPassword,
        // twilioPhoneNumber: '+19787235265',
        // fullPhoneNumber: '+19787235265',
        twilioPhoneNumber: '+61361601806',
        fullPhoneNumber: '+61400000000',
        receivedAdverts: true,
        status: 'active',
        statusReason: '',
        position: 'Business Owner',
        role: 'user',
        googleId: null,
        avatar: null,
        provider: 'local',
        tokenRefreshTime: new Date()
      });
      
      console.log('👤 Created test user:', testUser.email);
    }
    
    // 获取或创建用户（确保我们有正确的用户ID）
    const testUser = await UserModel.findOne({ email: 'john.doe@example.com' });
    
    if (!testUser) {
      throw new Error('Failed to create or find test user');
    }
    
    // 创建公司信息
    const testCompany = await CompanyModel.findOneAndUpdate(
      { user: testUser._id },
      {
        businessName: 'ABC Cleaning Services',
        email: 'info@abccleaning.com',
        abn: '12345678901',
        number: '+15559876543',
        address: {
          streetAddress: '123 Main Street',
          suburb: 'Sydney',
          state: 'NSW',
          postcode: '2000'
        },
        user: testUser._id
      },
      { upsert: true, new: true }
    );
    
    console.log('🏢 Created test company:', testCompany.businessName);
    
    // 创建服务列表
    const services = [
      {
        name: 'House Cleaning',
        description: 'Professional house cleaning service including dusting, vacuuming, and bathroom cleaning',
        price: 120.00,
        userId: testUser._id.toString(),
        isAvailable: true
      },
      {
        name: 'Garden Maintenance',
        description: 'Complete garden care including mowing, trimming, and plant care',
        price: 80.00,
        userId: testUser._id.toString(),
        isAvailable: true
      },
      {
        name: 'Plumbing Service',
        description: 'Emergency and routine plumbing repairs and maintenance',
        price: 150.00,
        userId: testUser._id.toString(),
        isAvailable: true
      },
      {
        name: 'Carpet Cleaning',
        description: 'Deep carpet cleaning and stain removal service',
        price: 100.00,
        userId: testUser._id.toString(),
        isAvailable: true
      },
      {
        name: 'Window Cleaning',
        description: 'Professional window cleaning for residential and commercial properties',
        price: 90.00,
        userId: testUser._id.toString(),
        isAvailable: true
      }
    ];
    
    const createdServices = await ServiceModel.insertMany(services);
    console.log('🔧 Created services:', createdServices.map(s => s.name));
    
    // 创建 Redis 测试数据（模拟 CallSkeleton）
    console.log('\n📞 Redis Test Data Structure:');
    console.log('CallSkeleton 示例:');
    console.log(JSON.stringify({
      callSid: 'CA' + randomUUID().replace(/-/g, '').substring(0, 32),
      services: createdServices.map(s => ({
        id: s._id.toString(),
        name: s.name,
        price: s.price,
        description: s.description
      })),
      company: {
        id: testCompany._id.toString(),
        name: testCompany.businessName,
        email: testCompany.email,
        phone: testCompany.number
      },
      user: {
        service: null,
        serviceBookedTime: null,
        userInfo: {}
      },
      history: [],
      servicebooked: false,
      confirmEmailsent: false,
      createdAt: new Date().toISOString()
    }, null, 2));
    
    console.log('\n🎯 Test Credentials:');
    console.log('Email: john.doe@example.com');
    console.log('Password: Admin123!');
    console.log('Phone: +19787235265');
    
    console.log('\n📋 Available Services for Testing:');
    createdServices.forEach((service, index) => {
      console.log(`${index + 1}. ${service.name} - $${service.price} - ${service.description}`);
    });
    
    console.log('\n🚀 Telephony Test Data Setup Complete!');
    console.log('You can now test the phone system with this data.');
    
  } catch (error) {
    console.error('❌ Error seeding telephony test data:', error);
  } finally {
    await connection.close();
    console.log('🔌 Disconnected from MongoDB');
  }
}

// 如果直接运行此文件
if (require.main === module) {
  seedTelephonyTestData();
}

export { seedTelephonyTestData }; 