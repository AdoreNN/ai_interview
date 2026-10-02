import type { ReactNode, SVGProps } from "react";

type IconName =
  | "plus"
  | "chat"
  | "file"
  | "settings"
  | "menu"
  | "close"
  | "arrow"
  | "upload"
  | "check"
  | "spark"
  | "logout"
  | "more"
  | "brain"
  | "chevron";

const paths: Record<IconName, ReactNode> = {
  plus: <path d="M12 5v14M5 12h14" />,
  chat: <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />,
  file: <path d="M6 2h8l4 4v16H6zM14 2v5h5M9 12h6M9 16h6" />,
  settings: <path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.6v-.2h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1z" />,
  menu: <path d="M4 7h16M4 12h16M4 17h16" />,
  close: <path d="m6 6 12 12M18 6 6 18" />,
  arrow: <path d="M5 12h14M13 6l6 6-6 6" />,
  upload: <path d="M12 16V4m0 0L7 9m5-5 5 5M5 14v6h14v-6" />,
  check: <path d="m5 12 4 4L19 6" />,
  spark: <path d="m12 3 1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5zM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z" />,
  logout: <path d="M10 4H5v16h5M14 8l4 4-4 4M8 12h10" />,
  more: <path d="M5 12h.01M12 12h.01M19 12h.01" />,
  brain: <path d="M9.5 4A3.5 3.5 0 0 0 6 7.5v.4A3.5 3.5 0 0 0 4 11a3.5 3.5 0 0 0 2 3.1v.4A3.5 3.5 0 0 0 9.5 18H12V6.5A2.5 2.5 0 0 0 9.5 4zM14.5 4A3.5 3.5 0 0 1 18 7.5v.4a3.5 3.5 0 0 1 2 3.1 3.5 3.5 0 0 1-2 3.1v.4a3.5 3.5 0 0 1-3.5 3.5H12V6.5A2.5 2.5 0 0 1 14.5 4zM8 9h4M12 13h4" />,
  chevron: <path d="m9 6 6 6-6 6" />,
};

export function Icon({ name, ...props }: SVGProps<SVGSVGElement> & { name: IconName }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      {paths[name]}
    </svg>
  );
}
