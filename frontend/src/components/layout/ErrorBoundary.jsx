import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('UI error boundary:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="ui-error-fallback glass" role="alert">
          <h2>Something went wrong displaying this view</h2>
          <p className="text-muted">
            {this.props.fallbackMessage ||
              'The investigation dashboard hit a rendering error. Try refreshing or open an older report from history.'}
          </p>
          {this.state.error?.message && (
            <pre className="ui-error-detail">{this.state.error.message}</pre>
          )}
          {this.props.onReset && (
            <button type="button" className="btn btn-primary mt-4" onClick={this.props.onReset}>
              Start new investigation
            </button>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
