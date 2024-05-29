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
      { ticker: 'USD', price: 190.93, perfDay: 0.19, perfMonth: 1.32 },
      { ticker: 'EUR', price: 151.84, perfDay: 0.19, perfMonth: 0.37 },
      { ticker: 'PORTFOLIO', price: 151.84, perfDay: 0.19, perfMonth: 0 },
      { ticker: 'INTEREST', price: 190.93, perfDay: 0.19, perfMonth: -0.99 },
      { ticker: 'GOLD', price: 151.84, perfDay: 0.19, perfMonth: -1.09 },
      // Add more data as needed
    ];
    this.datas = [
      { "name": "USD", "value": 1.32 },
      { "name": "EUR", "value": 0.37 },
      { "name": "PORTFOLIO", "value": 0.00 },
      { "name": "INTEREST", "value": -0.99 },
      { "name": "GOLD", "value": -1.09 },
    ];
  }

  ngOnInit(): void {}

}
