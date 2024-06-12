import { Component } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';


export interface PerformanceData {
  ticker: string;
  price: number;
  perfDay: number;
  perfMonth: number;
  // Add other performance metrics
}



@Component({
  selector: 'app-performance',
  templateUrl: './performance.component.html',
  styleUrl: './performance.component.css'
})
export class PerformanceComponent {
  datas: any[];
  displayedColumns: string[] = ['ticker', 'price', 'perfDay', 'perfMonth'];
  dataSourcex: PerformanceData[];

  constructor() {
    this.dataSourcex = [
      { ticker: 'USD', price: 1715.2, perfDay: 0.09, perfMonth: 2.94 },
      { ticker: 'EUR', price: 1643.30, perfDay: -0.33, perfMonth: -1.4 },
      { ticker: 'PORTFOLIO', price: 1666.65, perfDay: -1.95, perfMonth: 0 },
      { ticker: 'INTEREST', price: 1740.7, perfDay: 0.125, perfMonth: 3.75 },
      { ticker: 'GOLD', price: 1682.4, perfDay: 0.11, perfMonth: 1.09 },
      // Add more data as needed
    ];
    this.datas = [
      { "name": "USD", "value": 2.94 },
      { "name": "EUR", "value": -1.4 },
      { "name": "PORTFOLIO", "value": 0.00 },
      { "name": "INTEREST", "value": 3.75},
      { "name": "GOLD", "value": 1.09 },
    ];
  }

  ngOnInit(): void {}

}
