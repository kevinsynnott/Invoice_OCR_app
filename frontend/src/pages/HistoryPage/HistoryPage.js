import { useEffect, useState } from "react";

import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Grid } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import { useSnackbar } from "notistack";
import AppLayout from "../../components/AppLayout/AppLayout";
import InvoiceTable from "../../components/InvoiceTable/InvoiceTable";
import SummaryCard from "../../components/SummaryCard/SummaryCard";
import httpRequest from "../../httpRequest";
import { useStyles } from "./styles";

const HistoryPage = () => {
  const classes = useStyles();
  const [selectedInvoice, setSelectedInvoice] = useState({});
  const [invoicesData, setInvoicesData] = useState([]);
  const [isSummaryOpen, setIsSummaryOpen] = useState(false);
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    (async () => {
      await fetchInvoiceData();
    })();
  }, []);

  const fetchInvoiceData = async () => {
    try {
      const resp = await httpRequest.get(`http://${process.env.REACT_APP_BACKEND_HOSTNAME}:${process.env.REACT_APP_BACKEND_PORT}/get-invoices`);
      setInvoicesData(resp.data.invoices);
    } catch (error) {
      console.log("Error");
      enqueueSnackbar("Error fetching invoices", { variant: "error" });
    }
  };

  const openSummary = (invoiceData) => {
    setIsSummaryOpen(true);
    setSelectedInvoice(invoiceData);
  };

  const handleDataChange = () => {
    fetchInvoiceData();
  };

  return (
    <AppLayout>
      <Grid container>
        {!isSummaryOpen && (
          <div className={classes.table}>
            <InvoiceTable
              invoiceData={invoicesData}
              openSummary={openSummary}
              refreshInvoiceData={fetchInvoiceData}
            />
          </div>
        )}
      </Grid>
      {isSummaryOpen && (
        <div>
          <IconButton onClick={() => setIsSummaryOpen(false)}>
            <ArrowBackIcon fontSize="large" sx={{ color: "black", mb: "-30px" }} />
          </IconButton>
          <SummaryCard dataFromDB={selectedInvoice} dataChanged={handleDataChange} />
        </div>
      )}
    </AppLayout>
  );
};

export default HistoryPage;
