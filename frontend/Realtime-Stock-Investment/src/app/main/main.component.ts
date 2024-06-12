import { Component,Inject,OnInit,PLATFORM_ID} from '@angular/core';
import { Router } from '@angular/router';
import { StockInvestmentService } from '../services/stock-investment.service';
import { Observable, interval,Subscription  } from 'rxjs';
import { startWith, map } from 'rxjs/operators';
import { FormControl,FormGroup  } from '@angular/forms';
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { DatePipe } from '@angular/common';
import {ChartOptions, Color, TooltipLabelStyle} from 'chart.js';


@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrl: './main.component.css'
})

export class MainComponent {
  private updateSubscription!: Subscription;
  portfolioIds: number[] =[];
  currentPortfolioId: number = 0;
  currentSubTabIndex: number = 0;
  portfolioValues = {
    closedProfit: 0,
    dailyProfit: 0,
    marketValue: 0,
    openProfit: 0
  };
  stocks = [];
  transactions = [];
  portfolioColumns: string[] = ['symbol', 'amount', 'average_cost', 'lastPrice', 'marketValue', 'dailyStockProfit', 'dailyStockPercentageProfit', 'netStockProfit', 'netStockProfitPercentage'];
  transactionColumns: string[] = ['symbol', 'openDate','type', 'amount', 'openPrice', 'lastPrice', 'marketValue', 'dailyTransactionProfit', 'dailyTransactionPercentageProfit', 'netTransactionProfit', 'netTransactionProfitPercentage','actions'];
  formControl = new FormControl('');
  filterOptions!: Observable<string[]>;
  stockNames!: string[];
  stockName!: string;
  form: FormGroup = new FormGroup({
    date: new FormControl(),
    amount: new FormControl(),
    price: new FormControl(),
  });

  isStatisticsPageFirstTime = true;
  profitHistoryDates!: string[];
  profitHistoryData: any[] = [];
  lastMonthProfitHistoryDates!: string[];
  lastMonthProfitHistoryData : any[] = [];
  lastWeekProfitHistoryDates!: string[];
  lastWeekProfitHistoryData: any[] = [];
  currentGraphDates!: string[];
  currentGraphData: any[] = [];
  viewMode!: string;
  profitChartOptions: ChartOptions = this.getProfitChartOptions();

  pieChartLabels: string[] = [];
  pieChartData: number[] = [];
  pieChartOptions: ChartOptions = this.getStockDistributionChartOptions();
  constructor(private router: Router, private service: StockInvestmentService, @Inject(PLATFORM_ID) private platformId: Object, public datePipe: DatePipe)
  {
  }

  ngOnInit()
  { 
    this.service.getUserPortfolioIds().subscribe(response => {
      if(response.isSuccessful){
        this.portfolioIds = response.message;
        this.currentPortfolioId = this.portfolioIds[0];
        this.setProfitHistoryChart();
        this.setStockDistribution();

        if(this.currentPortfolioId != 0 ){ // && this.currentSubTabIndex == 0
          this.service.getPortfolio(this.currentPortfolioId).subscribe(response => {
            if(response.isSuccessful){
              this.stocks = response.stocks;
              this.portfolioValues = response;
            }
            else{
              this.service.showSnackBar(response.message,'error');
            }
          });
        }
  
        if(this.currentSubTabIndex == 1){ // Transactions
          this.service.getTransactions(this.currentPortfolioId).subscribe(response => {
            if(response.isSuccessful){
              this.transactions = response.message;
            }
            else{
              this.service.showSnackBar(response.message,'error');
            }
          });
        }

        this.service.getStockSymbols().subscribe(response => {
          if(response.isSuccessful){
            this.stockNames = response.message;
            this.filterOptions = this.formControl.valueChanges.pipe(
              startWith(''),map((value: any) => this.filter(value || ''))
            )
          }
          else{
            this.service.showSnackBar(response.message,'error');
          }
        });
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });

    this.updateSubscription = interval(5000).subscribe(() => {
      if(this.currentPortfolioId != 0 ){ // && this.currentSubTabIndex == 0
        this.service.getPortfolio(this.currentPortfolioId).subscribe(response => {
          if(response.isSuccessful){
            this.stocks = response.stocks;
            this.portfolioValues = response;
          }
          else{
            this.service.showSnackBar(response.message,'error');
          }
        });
      }

      if(this.currentSubTabIndex == 1){ // Transactions
        this.service.getTransactions(this.currentPortfolioId).subscribe(response => {
          if(response.isSuccessful){
            this.transactions = response.message;
          }
          else{
            this.service.showSnackBar(response.message,'error');
          }
        });
      }
    });
    
  }

  ngOnDestroy(){
    if (this.updateSubscription) {
      this.updateSubscription.unsubscribe();
    }
  }

  logOut() {
    if (this.updateSubscription) {
      this.updateSubscription.unsubscribe();
    }
    this.router.navigate(['/login']);
  }
  private filter(value:string) : string[] {
    const searchValue = value.toLocaleLowerCase();
    return this.stockNames.filter(option => option.toLocaleLowerCase().includes(searchValue));
  }

  loadTableData(portfolioId:any)
  { 
    this.currentSubTabIndex = 0;
    this.formControl.setValue(null);
    this.stockName = '';
    this.form.setValue({date: null,amount: null,price: null});
    this.currentPortfolioId = this.portfolioIds[portfolioId];
    this.service.getPortfolio(this.currentPortfolioId).subscribe(response => {
      if(response.isSuccessful){
        this.stocks = response.stocks;
        this.portfolioValues = response;

        if(this.currentPortfolioId != 0 ){ // && this.currentSubTabIndex == 0
          this.service.getPortfolio(this.currentPortfolioId).subscribe(response => {
            if(response.isSuccessful){
              this.stocks = response.stocks;
              this.portfolioValues = response;
            }
            else{
              this.service.showSnackBar(response.message,'error');
            }
          });
        }
        
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  onTabChange(event: any)
  {
    this.currentSubTabIndex = event;
    if(this.currentSubTabIndex == 1){ // Transactions
      this.service.getTransactions(this.currentPortfolioId).subscribe(response => {
        if(response.isSuccessful){
          this.transactions = response.message;
        }
        else{
          this.service.showSnackBar(response.message,'error');
        }
      });
    }  
  }

  getProfitChartOptions(): ChartOptions {
    const chartOptions: ChartOptions = {
      plugins: {
        tooltip: {
          position: 'nearest',
          mode: 'index',
          intersect: false,
          
          callbacks: {
            labelColor: function(context) : TooltipLabelStyle {
              let borderColor: Color = context.dataset.borderColor as Color || '#000';
              let backgroundColor: Color = context.dataset.backgroundColor as Color || '#fff'; 
              return {
                borderColor: borderColor,
                backgroundColor: backgroundColor,
              };
            },
            label: function(tooltipItem){ 
              var label = tooltipItem.dataset.label + ': '+ (tooltipItem.dataset?.data[tooltipItem.dataIndex] ?? ' ' );
              return label;
            }
          }
          
        }
      },
      hover: {
        mode: 'nearest',
        intersect: false
      },
      elements: {
        point: {
          radius: 4,
          hitRadius: 10,
          hoverRadius: 7,
        }
      },
    }; 
    return chartOptions;

  }

  getStockDistributionChartOptions(): ChartOptions {
    const chartOptions : ChartOptions = {
      responsive: true,
      maintainAspectRatio: false, // Chart'ın kendi aspect ratio'sunu korumasını engeller
      // Chart'ın boyutlarını kontrol etmek için gereken diğer seçenekler
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          // Tooltip ayarları
        }
      },
      // aspectRatio: 1, // Eğer bir aspect ratio belirlemek isterseniz
    };

    return chartOptions;
  }

  setProfitHistoryChart(){
    this.service.getProfitHistory(this.currentPortfolioId).subscribe(response => {
      if(response.isSuccessful){
        this.currentGraphData = [];
        this.currentGraphDates = [];
        this.profitHistoryDates = [];
        this.profitHistoryData = [];
        this.lastMonthProfitHistoryData = [];
        this.lastMonthProfitHistoryDates = [];
        this.lastWeekProfitHistoryData = [];
        this.lastWeekProfitHistoryDates = [];
        const maxLength = Math.max(...response.stocks.map((stock: { profits: string | any[]; }) => stock.profits.length));
        this.profitHistoryDates = response.stocks.find((stock: { profits: string | any[]; }) => stock.profits.length === maxLength).profits.map((profit: { date: string; }) => profit.date);
        for (let i = 0; i < response.stocks.length; i++) {
          let profitValues = response.stocks[i].profits.map((item: { profit: number; }) => item.profit);
          let extendedProfitValues = [...Array(maxLength - profitValues.length).fill(null), ...profitValues];
          let color = this.getRandomColor();
          this.profitHistoryData.push({ data: extendedProfitValues,
                                        label: response.stocks[i].symbol,
                                        borderColor: color,
                                        backgroundColor: color,
                                        pointRadius: 0,
                                        borderWidth: 4});                                 
        }
        
        if(maxLength <= 30){
         this.lastMonthProfitHistoryData = this.profitHistoryData;
         this.lastMonthProfitHistoryDates = this.profitHistoryDates; 
        }
        else{
          this.lastMonthProfitHistoryDates = this.profitHistoryDates.slice(-20);

          for (let index = 0; index < this.profitHistoryData.length; index++) {
            const element = JSON.parse(JSON.stringify(this.profitHistoryData[index]));
            this.lastMonthProfitHistoryData.push(element);
            this.lastMonthProfitHistoryData[index].data = element.data.slice(-20);
          }
        }

        if(maxLength <= 7){
          this.lastWeekProfitHistoryData = this.profitHistoryData;
          this.lastWeekProfitHistoryDates = this.profitHistoryDates;
        }
        else{
          this.lastWeekProfitHistoryDates = this.profitHistoryDates.slice(-5);

          for (let index = 0; index < this.profitHistoryData.length; index++) {
            const element = JSON.parse(JSON.stringify(this.profitHistoryData[index]));
            this.lastWeekProfitHistoryData.push(element);
            this.lastWeekProfitHistoryData[index].data = element.data.slice(-5);
          }
        }
        this.viewMode = "max";
        this.currentGraphData = this.profitHistoryData;
        this.currentGraphDates = this.profitHistoryDates;
      }
    });
  }

  setStockDistribution() {
    this.service.getStockDistribution(this.currentPortfolioId).subscribe(response => {
      if(response.isSuccessful){
        this.pieChartData = [];
        this.pieChartLabels = [];
        var stockDistribution = response.message;
        for (let index = 0; index < stockDistribution.length; index++) {
          this.pieChartLabels.push(stockDistribution[index].symbol);
          this.pieChartData.push(stockDistribution[index].distribution);       
        }
      }
    });
  }

  toggleViewMode(event: string) {
    if (event === 'lastWeek') {
      this.viewMode = 'lastWeek';
      this.currentGraphData = this.lastWeekProfitHistoryData;
      this.currentGraphDates = this.lastWeekProfitHistoryDates;
    } else if (event === 'lastMonth') {
      this.viewMode = 'lastMonth';
      this.currentGraphData = this.lastMonthProfitHistoryData;
      this.currentGraphDates = this.lastMonthProfitHistoryDates;
    } else if(event === 'max') {
      this.viewMode = 'max';
      this.currentGraphData = this.profitHistoryData;
      this.currentGraphDates = this.profitHistoryDates;
    }
  }

  getRandomColor(){
    const letters = '456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * letters.length)];
    }
    return color;
  }

  changeRowColor(value: number)
  {
    if(value == 0)
      return 'bold-text';
    return value > 0 ? 'positive-color' : 'negative-color';
  }

  onStockSelected(event: MatAutocompleteSelectedEvent): void{
    const selectedStockName = event.option.viewValue;
    this.stockName = selectedStockName;
    this.formControl.setValue(selectedStockName);
    this.form.setValue({date: null,amount: null,price: null});
  }

  onBuyClick(){
    this.service.buyStock(this.currentPortfolioId, this.stockName, this.form.value.amount, this.form.value.price, this.form.value.date).subscribe(response => {
      if(response.isSuccessful){
        this.service.showSnackBar(response.message,'success');
        this.setProfitHistoryChart();
        this.setStockDistribution();
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  onSellClick(){
    this.service.sellStock(this.currentPortfolioId, this.stockName, this.form.value.amount, this.form.value.price, this.form.value.date).subscribe(response => {
      if(response.isSuccessful){
        this.service.showSnackBar(response.message,'success');
        this.setProfitHistoryChart();
        this.setStockDistribution();
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  async onBlur(){
    await new Promise(resolve => setTimeout(resolve, 150));
    if(this.stockName != this.formControl.value && !this.stockNames.includes(this.formControl.value ?? ""))
      if(this.formControl.value == ''){
        this.stockName = '';
        this.formControl.setValue(null);
        this.form.setValue({date: null,amount: null,price: null});
      }
      else
        this.formControl.setValue(this.stockName);
  }

  deleteTransaction(transaction: any){
    this.service.deleteTransaction(transaction.transactionId).subscribe(response => {
      if(response.isSuccessful){
        this.service.showSnackBar(response.message,'success');
        this.setProfitHistoryChart();
        this.setStockDistribution();
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  dateFilter: (date: Date | null) => boolean = (d: Date | null): boolean => {
    if (d === null) {
      return false; // Disallow null values (no selection)
    }
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time part to the start of the day
    return d <= today; // Allow only days before today (inclusive)
  };
  addTab() {
   this.service.addPortfolio().subscribe(response => {
    if(response.isSuccessful){
      this.service.getUserPortfolioIds().subscribe(response => {
       if(response.isSuccessful){
         this.portfolioIds = response.message;
       }
       else{
         this.service.showSnackBar(response.message,'error');
       }
     });
    }
   });
   
  
  }
}
