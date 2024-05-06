import { Component } from '@angular/core';

interface Stock {
  ticker: string;
  last: number;
  change: number;
  volume: string;
}

interface Index {
  ticker: string;
  last: number;
  change: number;
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})

export class HomeComponent {
  indexItems = [
    { title: 'XU100', value: '9645,02', change: 0.00 },
    { title: 'XU30', value: '10429,05', change: 0.89 },
    { title: 'USDTRY', value: '32,55', change: 0.12 },
    { title: 'EURTRY', value: '34,85', change: 0.62 },
    { title: 'XAUUSD', value: '2324,50', change: -0.18 },
    // Diğer veriler
  ];

  gainers: Stock[] = [
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: 9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: 9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: 9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: 9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: 9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: 9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: 9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: 9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: 9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: 9.99, volume: '140.3M' },
    
    // Daha fazla örnek veri
  ];

  losers: Stock[] = [
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: -9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: -9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: -9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: -9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: -9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: -9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: -9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: -9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    { ticker: 'KZGYO', last: 23.1, change: -9.99, volume: '82.3M' },
    { ticker: 'REEDR', last: 45.1, change: -9.99, volume: '140.3M' },
    // Daha fazla örnek veri
  ];

  indices: Index[] = [
    { ticker: 'XUTEK', last: 45.2, change: 9.99},
    { ticker: 'XBANK', last: 23.1, change: 9.21 },
    { ticker: 'XBLSM', last: 5.2, change: 9.01 },
    { ticker: 'XELKT', last: 74.2, change: 8.85 },
    { ticker: 'XGIDA', last: 110.7, change: 7.73 },
    { ticker: 'XHOLD', last: 9.5, change: 7.21 },
    { ticker: 'XHARZ', last: 48.1, change: -6.95 },
    { ticker: 'XAKUR', last: 39.9, change: 6.40 },
    { ticker: 'XSPOR', last: 14.3, change: -6.35 },
    { ticker: 'XSGRT', last: 21.4, change: 6.20 },
    { ticker: 'XULAS', last: 98.5, change: 6.13 },
    { ticker: 'XTRZM', last: 27.9, change: 6.00 },
    { ticker: 'XGMYO', last: 7.3, change: 5.99 }
  ];

  constructor() { }

}
