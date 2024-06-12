import { Component } from '@angular/core';
import { StockInvestmentService } from '../services/stock-investment.service';
import { Subscription, interval } from 'rxjs';

interface Stock {
  ticker: string;
  last: number;
  change: number;
  volume: string;
}

interface Index {
  title: string;
  value: number;
  change: number;
}

interface TopIndex {
  title: string;
  value: number;
  change: number;
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})

export class HomeComponent {
  private updateSubscription!: Subscription;
  gainers!: Stock[];
  losers!: Stock[];
  indexItems!: TopIndex[];

  indices!: Index[];

  constructor(private service: StockInvestmentService) { }

  ngOnInit(){
    this.service.getAllBIST().subscribe(response => {
      if(response.isSuccessful){
        this.gainers = response.message.topGainers;
        this.losers = response.message.topLosers;
        this.indices = response.message.indices;
        this.indexItems = response.message.indexItems;
        this.indices[5].title = "XHOLD";
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });

    this.updateSubscription = interval(30000).subscribe(() => {
      this.service.getAllBIST().subscribe(response => {
        if(response.isSuccessful){
          this.gainers = response.message.topGainers;
          this.losers = response.message.topLosers;
          this.indices = response.message.indices;
          this.indexItems = response.message.indexItems;
          this.indices[5].title = "XHOLD";
        }
        else{
          this.service.showSnackBar(response.message,'error');
        }
      });
    });
  }

  ngOnDestroy(){
    if (this.updateSubscription) {
      this.updateSubscription.unsubscribe();
    }
  }

}
