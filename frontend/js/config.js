// frontend/js/config.js - API Configuration for Production
class Config {
    constructor() {
        this.environment = this.detectEnvironment();
        this.config = {
            development: {
                API_BASE: 'http://localhost:5000/api'
            },
            production: {
                API_BASE: 'https://mindease-backend-s59o.onrender.com/api'
            }
        };
    }

    detectEnvironment() {
        const hostname = window.location.hostname;
        return hostname === 'localhost' || hostname === '127.0.0.1' ? 'development' : 'production';
    }

    getApiBase() {
        return this.config[this.environment].API_BASE;
    }
}

// Create global variable
const appConfig = new Config();
const API_BASE = appConfig.getApiBase();
