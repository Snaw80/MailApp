import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Container, Typography, List, ListItem, Paper, Collapse, IconButton } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

// Function to decode MIME encoded-word syntax
const decodeMime = (text) => {
  return text.replace(/=\?utf-8\?Q\?(.*?)\?=/g, (match, p1) => {
    return p1.replace(/=([A-Fa-f0-9]{2})/g, (_, hex) => {
      return String.fromCharCode(parseInt(hex, 16));
    });
  });
};

function App() {
  const [whitelist, setWhitelist] = useState([]);
  const [newsletters, setNewsletters] = useState([]);
  const [expandedId, setExpandedId] = useState(null); // Track which newsletter is expanded

  useEffect(() => {
    fetchWhitelist();
    fetchNewsletters();
  }, []);

  const fetchWhitelist = async () => {
    try {
      const response = await axios.get('/whitelist');
      setWhitelist(response.data.whitelist);
    } catch (error) {
      console.error('Failed to fetch whitelist:', error);
    }
  };

  const fetchNewsletters = async () => {
    try {
      const response = await axios.get('/newsletters');
      const decodedNewsletters = response.data.newsletters.map(newsletter => ({
        ...newsletter,
        subject: decodeMime(newsletter.subject), // Decode the subject
      }));
      setNewsletters(decodedNewsletters);
    } catch (error) {
      console.error('Failed to fetch newsletters:', error);
    }
  };

  const handleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
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
            <div
              style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
              onClick={() => handleExpand(newsletter.id)}
            >
              <div>
                <Typography variant="h6">{newsletter.subject}</Typography>
                <Typography variant="subtitle1">{newsletter.from}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {new Date(newsletter.date).toLocaleString()}
                </Typography>
              </div>
              <IconButton>
                {expandedId === newsletter.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </div>

            {/* Collapsible content */}
            <Collapse in={expandedId === newsletter.id}>
              <div style={{ marginTop: '10px' }}>
                <div dangerouslySetInnerHTML={{ __html: newsletter.content }} />
              </div>
            </Collapse>
          </Paper>
        ))}
      </div>
    </Container>
  );
}

export default App;