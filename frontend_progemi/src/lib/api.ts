// lib/api.ts

import axios from 'axios';

import Cookies from 'js-cookie';


export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE,
  withCredentials: true,  
});

api.interceptors.request.use(cfg => {
  
  const token = Cookies.get('access_token');

  if (token) cfg.headers['Authorization'] = `Bearer ${token}`;
  
  return cfg;
});
