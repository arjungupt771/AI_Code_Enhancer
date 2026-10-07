import React from "react";

export default class AppErrorBoundary
  extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(
    error
  ) {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error, info) {
    console.error(
      "Application error:",
      error,
      info
    );
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
          <div className="max-w-lg w-full bg-white rounded-xl border border-red-200 shadow-sm p-6">
            <div className="text-xl font-semibold text-gray-900">
              The application encountered an error.
            </div>

            <p className="mt-2 text-sm text-gray-600">
              You can try resetting the current
              application state.
            </p>

            <button
              onClick={this.handleReset}
              className="mt-5 px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
            >
              Try again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
