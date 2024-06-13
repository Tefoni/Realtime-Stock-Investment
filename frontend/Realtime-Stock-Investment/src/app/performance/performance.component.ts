import { Component } from '@angular/core';
import { MatTableDataSource } from '@angular/material/table';
import { StockInvestmentService } from '../services/stock-investment.service';


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
  datas: any[] = [];
  displayedColumns: string[] = ['ticker', 'price', 'perfDay', 'perfMonth'];
  dataSourcex: PerformanceData[] = [];


  constructor(private service: StockInvestmentService) {
  }

  ngOnInit(): void {
    this.service.performance().subscribe(response => {
      if(response.isSuccessful){
        this.dataSourcex = response.message;
        this.dataSourcex.push({ ticker: 'PORTFOLIO', price: 1666.65, perfDay: -1.95, perfMonth: 0 });

        this.dataSourcex.forEach(data => {
          this.datas.push({"name": data.ticker,"value": data.perfMonth});
        });
        this.datas = [...this.datas];
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });

  }

}
