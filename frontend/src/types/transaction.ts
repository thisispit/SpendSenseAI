export interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  category: string;
  confidence: number;
  source: "OCR" | "Manual";
  account: string;
  merchant?: string;
  type: "CREDIT" | "DEBIT";
}
