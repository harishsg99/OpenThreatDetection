import React from "react";
import {
  Button,
  Container,
  Grid,
  Header,
  Image,
  List,
  Card,
  Icon,
  Segment
} from "semantic-ui-react";
import { Link } from "react-router-dom";
import AI from "../assets/images/ai.svg";

const HomepageLayout = () => (
  <React.Fragment>
    <Segment style={{ padding: "8em 0em" }} vertical>
      <Container textAlign="center">
        <Grid container stackable verticalAlign="center">
          <Grid.Row verticalAlign="middle">
            <Grid.Column width={8} textAlign="center">
              <Header as="h3" style={{ fontSize: "3em" }}>
                A powerful suite of apis to make developer's routine work easier
            </Header>
              <p style={{ fontSize: "2em" }}>
                Automate your next app developement experience with our powerful suite of apis
            </p>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column textAlign="center">
              <Link to="/login">
                <Button primary size="huge">
                  Get started
              </Button>
              </Link>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Container>
    </Segment>
    <Segment style={{ padding: "8em 0em" }} vertical>
      <Container>
        <Header as="h3" style={{ fontSize: "2em" }} textAlign="center">
          API Catalogue
        </Header>
        <Grid columns={3} divided>
          <Grid.Row>
            <Grid.Column>
              <Card>
                <Card.Content header='Email Finder API' />
                <Card.Content description={'Find anyone email address using their first name , last name and company domain'} />
              </Card>
            </Grid.Column>
            <Grid.Column>
              <Card>
                <Card.Content header='Email verification and validation API' />
                <Card.Content description={'Validate and verify any email quickly and reliably'} />
              </Card>
            </Grid.Column>
            <Grid.Column>
              <Card>
                <Card.Content header='Phone number validation API' />
                <Card.Content description={'Validate any phone number quickly'} />
              </Card>
            </Grid.Column>
          </Grid.Row>

          <Grid.Row>
            <Grid.Column>
              <Card>
                <Card.Content header='linkchecking API' />
                <Card.Content description={'Find number of working and non working links in your website '} />
              </Card>
            </Grid.Column>
            <Grid.Column>
              <Card>
                <Card.Content header='Grammer checking API' />
                <Card.Content description={'Find the spelling and grammatical mistake in a sentence or paragraph '} />
              </Card>
            </Grid.Column>
            <Grid.Column>
              <Card>
                <Card.Content header='IP finding API' />
                <Card.Content description={'Get cordinates of the ip address'} />
              </Card>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column>
              <Card>
                <Card.Content header='Public Holiday API' />
                <Card.Content description={'Get holidays for any country at any time'} />
              </Card>
            </Grid.Column>
            <Grid.Column>
              <Card>
                <Card.Content header='Web scraper API' />
                <Card.Content description={'Scrape any website and extract data'} />
              </Card>
            </Grid.Column>
            <Grid.Column>
              <Card>
                <Card.Content header='Link preview API' />
                <Card.Content description={'Get preview of any website at any time'} />
              </Card>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Container>
    </Segment>
    <Segment style={{ padding: "8em 0em" }} vertical>
      <Container text>
        <Header as="h3" style={{ fontSize: "2em" }}>
          Try our API
        </Header>
        <p style={{ fontSize: "1.33em" }}>
          Test our API for free for the new two weeks. No credit card required.
        </p>
        <Link to="/login">
          <Button positive size="large">
            Start my free trial
          </Button>
        </Link>
        <Header as="h3" style={{ fontSize: "2em" }}>
          Pricing
        </Header>
        <p style={{ fontSize: "1.33em" }}>
          Pay for what you use, at $0.05 per request.
        </p>
        <Link to="/login">
          <Button primary size="large">
            Start now
          </Button>
        </Link>
      </Container>
    </Segment>
    <Segment inverted vertical style={{ padding: "5em 0em" }}>
      <Container>
        <Grid divided inverted stackable>
          <Grid.Row>
            <Grid.Column width={3}>
              <Header inverted as="h4" content="About" />
              <List link inverted>
                <List.Item as="a">Sitemap</List.Item>
                <List.Item as="a">Contact Us</List.Item>
              </List>
            </Grid.Column>
            <Grid.Column width={3}>
              <Header inverted as="h4" content="Services" />
              <List link inverted>
                <List.Item as="a">FAQ</List.Item>
                <List.Item as="a">Pricing</List.Item>
                <List.Item as="a">API</List.Item>
              </List>
            </Grid.Column>
            <Grid.Column width={7}>
              <Header as="h4" inverted>
                SimplyAPI
              </Header>
              <p>Made with ♥ from India</p>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Container>
    </Segment>
  </React.Fragment>
);

export default HomepageLayout;
