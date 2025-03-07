import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Container, Typography, List, ListItem, Paper } from '@mui/material';

function App() {
  const [whitelist, setWhitelist] = useState([]);
  const [newsletters, setNewsletters] = useState([]);

  useEffect(() => {
    fetchWhitelist();
    fetchNewsletters();
  }, []);

  const fetchWhitelist = async () => {
    try
    {
      const response = await axios.get('/whitelist');
      setWhitelist(response.data.whitelist);
    }
    catch (error)
    {
      console.error('Failed to fetch whitelist:', error);
    }
  };

  const fetchNewsletters = async () => {
    try
    {
      const response = await axios.get('/newsletters');
      setNewsletters(response.data.newsletters);
    }
    catch (error)
    {
      console.error('Failed to fetch newsletters:', error);
    }
  };

  return (
    <Container>
      <Typography variant="h3" gutterBottom>
        Mes Newsletters
      </Typography>
      
      <Paper elevation={3} style={{ padding: '20px', marginBottom: '20px' }}>
        <Typography variant="h5">Whitelist</Typography>
        <List>
          {whitelist.map(email => (
            <ListItem key={email}>{email}</ListItem>
          ))}
        </List>
      </Paper>

      <div>
        {newsletters.map(newsletter => (
          <Paper key={newsletter.id} elevation={2} style={{ padding: '20px', margin: '10px 0' }}>
            <Typography variant="h6">{newsletter.subject}</Typography>
            <Typography variant="subtitle1">{newsletter.from}</Typography>
            <Typography variant="body2" color="textSecondary">
              {new Date(newsletter.date).toLocaleString()}
            </Typography>
            <div dangerouslySetInnerHTML={{ __html: newsletter.content }} />
          </Paper>
        ))}
      </div>
    </Container>
  );
}

export default App;